# AI-generated code: written with an AI assistant (Claude) during the NASA Space Apps Challenge 2026 hackathon.
# AI-generated (Claude Code, 2026-11-15) for the Space Apps team. Not human-reviewed.
# Final recount for the video plan. Read-only on the repository and the pilot disk; no network.
# It re-derives, from the scratch video index (names only) and the repository tables:
#   - link states in the vocabulary of docs/raw_data_design/design.md (3.1, link 4)
#   - counted tests with a video, per question, by link state
#   - the same per scenario placement (inside / cannot_be_placed_from_table / ...)
#   - the ISS flammability shortlist with the corrected main-view definition
# Usage: python3 -I video_final.py   (writes final/video_final.json, final/video_links_states.csv,
#        final/shortlist_iss_P1_main_view.csv next to this script)
import csv, json, os, re, collections, sys

REPO = '/Users/choidol/Desktop/NASA/NASA_RAPID'
SP = '/private/tmp/claude-501/-Users-choidol-Desktop-NASA/dbfa83f0-2503-422b-8628-6630f4ec57a9/scratchpad/videodesign'
PILOT = '/Users/choidol/Desktop/NASA/video_pilot/raw_bass2'
OUT = os.path.join(SP, 'final')

vid = list(csv.DictReader(open(os.path.join(SP, 'video_index_names.csv'), newline='')))
tests = {r['test_id']: r for r in csv.DictReader(open(os.path.join(REPO, 'data/pipeline/tests.csv'), newline=''))}
need = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(REPO, 'data/pipeline/need_tests.csv'), newline='')):
    need[r['need_id']][r['test_id']] = r
sc = collections.defaultdict(dict)
for r in csv.DictReader(open(os.path.join(REPO, 'data/pipeline/scenario_tests.csv'), newline='')):
    sc[r['scenario_id']][r['test_id']] = r
pilot = set(os.listdir(PILOT))

norm = lambda s: re.sub(r'[\s_]+', '', (s or '')).upper()

def ids_of(v):
    d = {}
    for part in v['identifiers'].split(';'):
        if '=' in part:
            k, x = part.split('=', 1)
            d[k.strip()] = x.strip()
    return d

def placement(s):  # the rule of docs/raw_data_design/prototype/chain_proto.py
    o, p = s['o2_match'], s['pressure_match']
    if o == 'out' or p == 'out':
        return 'outside_by_recorded_value'
    if o == 'in' and p == 'in':
        return 'inside'
    if o == 'not_ambient':
        return 'oxygen_of_oxidizer_stream'
    return 'cannot_be_placed_from_table'

NAME_KEYS = ('testpoint', 'test', 'cir_testpoint')
FOLDER_KEYS = ('folder_testpoint', 'folder_test', 'folder_cir')

def link_state(v):
    """Returns (tie_scope, link_state, labels agreeing, labels against, second_label_scope).
    Vocabulary of docs/raw_data_design/design.md 3.1 link 4:
    two_labels_agree / one_label / labels_disagree / id_not_in_table / day_only / none.
    Labels used: the NASA identifier in the file name; the PSI folder label.
    For BASS-II the GMT day and sample number in the name are compared with the tied table row as a
    consistency check (they can also fit other rows, so they are not counted as a second label)."""
    d = ids_of(v)
    tl = v['tie_level']
    inv = v['investigation']
    name_id = next((d[k] for k in NAME_KEYS if d.get(k)), '')
    folder_id = next((d[k] for k in FOLDER_KEYS if d.get(k)), '')
    aux = d.get('check_gmt_sample', '')
    labels, against, scope2 = [], [], ''
    if tl == 'single_test':
        src = v['identifier_source']
        if src.startswith('folder'):
            labels.append('folder_id')
            # a readable identifier in the name that differs from the folder's is a disagreement
            if name_id and norm(name_id) != norm(folder_id):
                against.append('name_id')
            if inv == 'PSI-159' and not name_id and re.search(r'udp_+\d{4,6}[A-Z]\d', v['file_name']):
                against.append('name_id_unreadable_or_mistyped')
        else:
            labels.append('name_id')
            if folder_id:
                if norm(folder_id) == norm(name_id):
                    labels.append('folder_id')
                elif inv == 'PSI-25' and re.fullmatch(re.escape(norm(folder_id)) + '[AB]', norm(name_id)):
                    scope2 = 'folder names the test number without the run letter (both runs of the sample)'
                else:
                    against.append('folder_id')
        if inv == 'PSI-25' and aux and aux != 'agree':
            against.append('name_gmt_or_sample_vs_table')
        if against:
            st = 'labels_disagree'
        elif len(labels) >= 2:
            st = 'two_labels_agree'
        else:
            st = 'one_label'
        return 'test', st, labels, against, scope2
    if tl in ('run', 'day', 'several_days'):
        return tl, 'day_only', [], [], ''
    n = v['notes']
    if re.search(r'not in the|not among|ends in 2011|no table row|neither the', n) or '2013-2014' in n:
        return 'none', 'id_not_in_table', [], [], ''
    return 'none', 'none', [], [], ''

rows = []
for v in vid:
    scope, st, lab, ag, sc2 = link_state(v)
    v['_scope'], v['_state'], v['_labels'], v['_against'], v['_scope2'] = scope, st, lab, ag, sc2
    rows.append(dict(investigation=v['investigation'], file_name=v['file_name'], bytes=v['bytes'], folder=v['folder'],
                     tie_scope=scope, link_state=st, test_id=v['test_id'], labels_agreeing=' '.join(lab),
                     labels_against=' '.join(ag), second_label_scope=sc2, clip_words=v['clip_words'], notes=v['notes'],
                     name_folder_conflict=v['name_folder_conflict'], psi_file_id=v['psi_file_id']))
with open(os.path.join(OUT, 'video_links_states.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)

res = {'_meta': {'made_by': 'AI-generated (Claude Code), 2026-11-15, not human-reviewed',
                 'inputs': ['videodesign/video_index_names.csv', 'data/pipeline/tests.csv', 'need_tests.csv', 'scenario_tests.csv']}}
res['totals'] = {'videos': len(vid), 'bytes': sum(int(v['bytes']) for v in vid)}
res['tie_scope'] = {k: {'videos': n, 'bytes': sum(int(v['bytes']) for v in vid if v['_scope'] == k)}
                    for k, n in collections.Counter(v['_scope'] for v in vid).items()}
res['link_state'] = {k: {'videos': n, 'bytes': sum(int(v['bytes']) for v in vid if v['_state'] == k)}
                     for k, n in collections.Counter(v['_state'] for v in vid).items()}
res['link_state_by_investigation'] = {}
for inv in sorted({v['investigation'] for v in vid}, key=lambda s: int(s.split('-')[1])):
    c = collections.Counter(v['_state'] for v in vid if v['investigation'] == inv)
    res['link_state_by_investigation'][inv] = dict(c)
res['labels_disagree_list'] = [dict(investigation=v['investigation'], file_name=v['file_name'], tied_to=v['test_id'],
                                    agree=v['_labels'], against=v['_against'], conflict=v['name_folder_conflict'], notes=v['notes'])
                               for v in vid if v['_state'] == 'labels_disagree']
res['one_label_by_investigation'] = dict(collections.Counter(v['investigation'] + ':' + (v['_labels'][0] if v['_labels'] else '?') for v in vid if v['_state'] == 'one_label'))

# tests by best link state
RANK = {'two_labels_agree': 0, 'one_label': 1, 'labels_disagree': 2}
best = {}
files_of = collections.defaultdict(list)
for v in vid:
    if v['_scope'] == 'test' and v['test_id']:
        files_of[v['test_id']].append(v)
        if v['test_id'] not in best or RANK[v['_state']] < RANK[best[v['test_id']]]:
            best[v['test_id']] = v['_state']
res['tests_with_video_by_best_state'] = dict(collections.Counter(best.values()))
res['tests_total'] = len(tests)
res['tests_by_investigation_best_state'] = {}
for t, s in best.items():
    inv = tests[t]['investigation_id'] if t in tests else '?'
    res['tests_by_investigation_best_state'].setdefault(inv, collections.Counter())[s] += 1
res['tests_by_investigation_best_state'] = {k: dict(v) for k, v in res['tests_by_investigation_best_state'].items()}

def count_block(tids):
    out = collections.Counter()
    fl, by = 0, 0
    for t in tids:
        s = best.get(t)
        out[s or 'no_video_of_the_test'] += 1
    two = [t for t in tids if best.get(t) == 'two_labels_agree']
    fs = [v for t in two for v in files_of[t] if v['_state'] == 'two_labels_agree']
    return dict(tests=len(tids), **out, files_two_labels=len(fs), bytes_two_labels=sum(int(v['bytes']) for v in fs),
                by_investigation=dict(collections.Counter(tests[t]['investigation_id'] + ':' + (best.get(t) or 'no_video') for t in tids)))

res['counted_tests_with_video'] = {}
for n in sorted(need):
    counted = [t for t, r in need[n].items() if r['objective_link'] == 'stated']
    res['counted_tests_with_video'][n] = count_block(counted)

res['by_scenario_placement'] = {}
for s in ('iss', 'lunar_habitat'):
    res['by_scenario_placement'][s] = {}
    allp = collections.defaultdict(list)
    for t in tests:
        allp[placement(sc[s][t])].append(t)
    res['by_scenario_placement'][s]['all_tests'] = {p: count_block(ts) for p, ts in allp.items()}
    for n in sorted(need):
        counted = [t for t, r in need[n].items() if r['objective_link'] == 'stated']
        bp = collections.defaultdict(list)
        for t in counted:
            pl = placement(sc[s][t])
            if pl == 'cannot_be_placed_from_table':
                pl += ' (oxygen %s, pressure %s)' % (sc[s][t]['o2_match'], sc[s][t]['pressure_match'])
            bp[pl].append(t)
        res['by_scenario_placement'][s][n] = {p: count_block(ts) for p, ts in bp.items()}

# ---- BASS-II views (corrected definition: main view = not second view, not still sequence,
#      not a post-burn picture, not a rack or monitor view; loss-of-signal portions stay in)
def view(v):
    """Clip kind from the words in the name only (no picture looked at)."""
    w = set(re.split(r'[;, ]+', v['clip_words'])) - {''}
    n = v['file_name']
    if 'second_view' in w: return 'second_view'
    if 'still_sequence' in w: return 'still_sequence'
    if 'post_burn_picture' in w: return 'other:post_burn_picture'
    if 'rack_or_monitor_view' in w or re.search(r'lab-camera|over-the-shoulder', n): return 'other:rack_monitor_or_other_camera'
    if 'loss_of_signal_portion' in w: return 'main:portion_during_loss_of_signal'
    if 'ignition_attempt' in w: return 'main:ignition_attempt'
    if 'part_of_recording' in w: return 'main:part'
    if w & {'shifted_video', 'flame_blowoff_clip', 'stream_recording'} or not re.search(r'BASS_GMT\d+_SAMPLE_\d+_TEST', n): return 'main:excerpt_or_other_named_clip'
    return 'main:whole_recording_no_extra_words'
b2 = [v for v in vid if v['investigation'] == 'PSI-25']
for v in b2: v['_view'] = view(v)
res['bass2_views'] = {k: {'files': n, 'bytes': sum(int(v['bytes']) for v in b2 if v['_view'] == k),
                          'tests': len({v['test_id'] for v in b2 if v['_view'] == k})}
                      for k, n in collections.Counter(v['_view'] for v in b2).items()}
res['bass2_clip_words'] = dict(collections.Counter(v['clip_words'] for v in b2))

def shortlist(name, tids, write=None):
    main = [v for v in b2 if v['test_id'] in tids and v['_view'].startswith('main:')]
    plain = [v for v in main if v['_view'] == 'main:whole_recording_no_extra_words']
    los = [v for v in main if v['_view'] != 'main:whole_recording_no_extra_words']
    two = [v for v in main if v['_state'] == 'two_labels_agree']
    notdisk = [v for v in main if v['file_name'] not in pilot]
    gd = lambda v: (re.search(r'GMT[_ ]?(\d+)', v['file_name']) or [None, 'none'])[1]
    o = dict(tests=len(tids), tests_with_main_view=len({v['test_id'] for v in main}),
             tests_with_plain_main_only_definition=len({v['test_id'] for v in plain}),
             files=len(main), bytes=sum(int(v['bytes']) for v in main),
             plain_files=len(plain), plain_bytes=sum(int(v['bytes']) for v in plain),
             los_files=len(los), los_bytes=sum(int(v['bytes']) for v in los),
             los_names=[v['file_name'] for v in los],
             files_two_labels_agree=len(two), bytes_two_labels_agree=sum(int(v['bytes']) for v in two),
             states=dict(collections.Counter(v['_state'] for v in main)), kinds=dict(collections.Counter(v['_view'] for v in main)),
             tests_by_best_state_of_main=dict(collections.Counter(min((RANK[v['_state']] for v in main if v['test_id']==t), default=9) for t in tids)),
             on_disk_files=len(main) - len(notdisk), not_on_disk_files=len(notdisk),
             not_on_disk_bytes=sum(int(v['bytes']) for v in notdisk),
             not_on_disk_days=len({gd(v) for v in notdisk}),
             tests_without_main_view=sorted(t for t in tids if t not in {v['test_id'] for v in main}),
             transcribed_tests=sorted({v['test_id'] for v in main if v['file_name'] in pilot}),
             all_views_files=len([v for v in b2 if v['test_id'] in tids]),
             all_views_bytes=sum(int(v['bytes']) for v in b2 if v['test_id'] in tids),
             tests_with_any_video=len({v['test_id'] for v in b2 if v['test_id'] in tids}))
    if write:
        with open(os.path.join(OUT, write), 'w', newline='') as f:
            w = csv.writer(f)
            w.writerow(['# AI-generated (Claude Code) 2026-11-15 from PSI listing names; not human-reviewed. A tie says which recording belongs to a test row; it is not a measurement.'])
            w.writerow(['test_id', 'file_name', 'bytes', 'psi_investigation', 'clip_kind_from_name', 'link_state', 'labels_agreeing', 'labels_against', 'second_label_scope', 'on_team_disk_and_transcribed', 'psi_file_id'])
            for v in sorted(main, key=lambda v: (v['test_id'], v['file_name'])):
                w.writerow([v['test_id'], v['file_name'], v['bytes'], v['investigation'],
                            v['_view'].split(':',1)[1].replace('_',' '),
                            v['_state'], ' '.join(v['_labels']), ' '.join(v['_against']), v['_scope2'],
                            'yes' if v['file_name'] in pilot else 'no', v['psi_file_id']])
    return o

P1 = {t for t, r in need['P1'].items() if r['objective_link'] == 'stated'}
S1 = {t for t, r in need['S1'].items() if r['objective_link'] == 'stated'}
D1 = {t for t, r in need['D1'].items() if r['objective_link'] == 'stated'}
iss = sc['iss']
o2in = lambda t: iss[t]['o2_match'] == 'in' and iss[t]['pressure_match'] == 'not_recorded'
res['shortlists'] = {
    'iss_P1_oxygen_inside_pressure_not_in_table_all': {'counted_tests': len([t for t in P1 if o2in(t)]),
        'by_investigation': dict(collections.Counter(tests[t]['investigation_id'] for t in P1 if o2in(t)))},
    'iss_P1_bass2': shortlist('iss P1 BASS-II', {t for t in P1 if o2in(t) and t.startswith('BASS2')}, 'shortlist_iss_P1_main_view.csv'),
    'iss_D1_bass2': shortlist('iss D1 BASS-II', {t for t in D1 if o2in(t) and t.startswith('BASS2')}),
    'iss_S1_bass2': shortlist('iss S1 BASS-II', {t for t in S1 if o2in(t) and t.startswith('BASS2')}),
    'P1_counted_bass2': shortlist('P1 BASS-II', {t for t in P1 if t.startswith('BASS2')}),
    'all_bass2': shortlist('all BASS-II', {t for t in tests if t.startswith('BASS2')}),
}
# lunar: tests inside the ranges and their videos
lun = sc['lunar_habitat']
inside = [t for t in tests if placement(lun[t]) == 'inside']
res['lunar_inside'] = {'tests': len(inside),
    'by_investigation': dict(collections.Counter(tests[t]['investigation_id'] for t in inside)),
    'with_video_by_state': dict(collections.Counter(best.get(t, 'no_video_of_the_test') for t in inside)),
    'video_files': [dict(test=t, file=v['file_name'], bytes=int(v['bytes']), state=v['_state']) for t in inside for v in files_of.get(t, [])],
    'S1_counted_inside': len([t for t in inside if t in S1]),
    'S1_counted_inside_with_video': len([t for t in inside if t in S1 and t in best])}
res['lunar_inside']['video_bytes'] = sum(x['bytes'] for x in res['lunar_inside']['video_files'])
issin = [t for t in tests if placement(iss[t]) == 'inside']
res['iss_inside'] = {'tests': len(issin), 'by_investigation': dict(collections.Counter(tests[t]['investigation_id'] for t in issin)),
    'with_video_by_state': dict(collections.Counter(best.get(t, 'no_video_of_the_test') for t in issin)),
    'S1_counted_inside': len([t for t in issin if t in S1]),
    'S1_counted_inside_states': dict(collections.Counter(best.get(t, 'no_video_of_the_test') for t in issin if t in S1)),
    'S1_counted_inside_video_bytes': sum(int(v['bytes']) for t in issin if t in S1 for v in files_of.get(t, []))}
# overlay scope: files of the four investigations with the overlay in a sampled frame
ov = [v for v in vid if v['investigation'] in ('PSI-25', 'PSI-26', 'PSI-106', 'PSI-107')]
res['overlay_investigations'] = {'files': len(ov), 'bytes': sum(int(v['bytes']) for v in ov)}
res['ext'] = dict(collections.Counter(v['extension'] for v in vid))
# videos tied to counted tests (any question), any link state
counted_any = set().union(*[{t for t, r in need[n].items() if r['objective_link'] == 'stated'} for n in need])
cv = [v for v in vid if v['_scope'] == 'test' and v['test_id'] in counted_any]
res['videos_tied_to_counted_tests'] = {'files': len(cv), 'bytes': sum(int(v['bytes']) for v in cv),
    'by_investigation': dict(collections.Counter(v['investigation'] for v in cv)), 'by_ext': dict(collections.Counter(v['extension'] for v in cv))}
json.dump(res, open(os.path.join(OUT, 'video_final.json'), 'w'), indent=1, default=list)
print(json.dumps(res, indent=1, default=list)[:200])
