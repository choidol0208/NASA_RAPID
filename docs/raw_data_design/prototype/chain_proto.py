# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
"""Prototype of the question chain for one scenario (read-only on the repository).

question (need at an environment) -> quantities -> where each lives -> which file groups -> bytes.
Usage: python3 chain_proto.py <repo> <scenario_id> <out_dir>
Reads: data/pipeline/{tests,scenario_tests,need_tests,gap_states}.csv, pipeline/spec/needs.json
Writes: <out_dir>/chain_<scenario>.csv and prints a summary.
"""
import csv, json, sys, collections, os

repo, scen, out = sys.argv[1], sys.argv[2], sys.argv[3]
P = os.path.join(repo, 'data', 'pipeline')
T = {r['test_id']: r for r in csv.DictReader(open(os.path.join(P, 'tests.csv')))}
S = {r['test_id']: r for r in csv.DictReader(open(os.path.join(P, 'scenario_tests.csv'))) if r['scenario_id'] == scen}
NT = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(P, 'need_tests.csv'))):
    NT[r['need_id']][r['test_id']] = r['objective_link']
G = collections.defaultdict(list)
for r in csv.DictReader(open(os.path.join(P, 'gap_states.csv'))):
    G[(r['investigation_id'], r['variable'])].append(r)
needs = json.load(open(os.path.join(repo, 'pipeline', 'spec', 'needs.json')))['needs']


def placement(t):
    s = S[t]
    o, p = s['o2_match'], s['pressure_match']
    if o == 'out' or p == 'out':
        return 'outside_by_table_value'
    if o == 'in' and p == 'in':
        return 'inside'
    if o == 'not_ambient':
        return 'oxygen_is_of_oxidizer_stream'
    return 'cannot_be_placed_from_table'  # at least one of the two not recorded, none out


def raw_state(inv, var):
    """state of the tests of this investigation that have no table value for var"""
    for r in G[(inv, var)]:
        if r['state'] != 'in_table':
            return r
    return None


rows = []
for n in needs:
    nid = n['id']
    scope = n.get('scope', {}).get('fuel_phase')
    insc = [t for t, r in T.items() if (not scope or r['fuel_phase'] in scope)]
    counted = {t for t, l in NT[nid].items() if l == 'stated'}
    roles = [('required', v) for v in n['conditions_required']] + [('useful', v) for v in n.get('conditions_useful', [])] + [('outcome', v) for v in n['outcomes_any']]
    pl = {t: placement(t) for t in insc}
    for role, var in roles:
        agg = collections.defaultdict(lambda: [0, 0])
        for t in insc:
            r = T[t]
            if var == 'gravity_level' or r.get(var, '') != '':
                loc = ('table_cell', '', '', '', '')
            else:
                g = raw_state(r['investigation_id'], var)
                if g is None:
                    loc = ('not_classified', '', '', '', '')
                elif g['state'] == 'column_in_sampled_raw_file':
                    loc = ('raw_file_column', g['column_is'], g['file_groups'], g['files'], g['bytes'])
                elif g['state'] == 'documented_only':
                    loc = ('document_sentence', g['documented_by'], '', '', '')
                else:
                    loc = ('not_found_in_sampled_files', '', '', '', '')
            k = (r['investigation_id'], pl[t]) + loc
            agg[k][0] += 1
            agg[k][1] += (t in counted)
        for k, (a, c) in sorted(agg.items()):
            rows.append(dict(scenario_id=scen, need_id=nid, role=role, variable=var, investigation_id=k[0], placement=k[1],
                             location=k[2], column_is_or_doc=k[3], file_groups=k[4], files=k[5], bytes=k[6],
                             in_scope_tests=a, counted_tests=c))

os.makedirs(out, exist_ok=True)
fn = os.path.join(out, f'chain_{scen}.csv')
with open(fn, 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
print('wrote', fn, len(rows), 'rows')

# summary per need: placement of in-scope and counted tests
for n in needs:
    nid = n['id']
    scope = n.get('scope', {}).get('fuel_phase')
    insc = [t for t, r in T.items() if (not scope or r['fuel_phase'] in scope)]
    counted = {t for t, l in NT[nid].items() if l == 'stated'}
    c1 = collections.Counter(placement(t) for t in insc)
    c2 = collections.Counter(placement(t) for t in insc if t in counted)
    print(nid, 'in scope', len(insc), dict(c1), '| counted', len(counted), dict(c2))
    # location summary by placement for each variable
    by = collections.defaultdict(lambda: collections.Counter())
    for r in rows:
        if r['need_id'] == nid:
            by[(r['role'], r['variable'])][(r['placement'], r['location'])] += r['in_scope_tests']
    for k, v in by.items():
        print('   ', k, dict(v))
