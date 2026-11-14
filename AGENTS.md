# AI working guidelines — NASA Space Apps Challenge 2026

Current phase: HACK
(Only a person changes this line. The value is one of PREP / HACK / CLOSED.)
(2026-11-14 09:00 KST, changed to HACK when the user declared the start. The submission deadline is 2026-11-15 23:59 KST.)

## Situation

This repository is for taking part in the 2026 NASA Space Apps Challenge (11/14–15, Seoul Local Event).
The chosen challenge is "Flame in Freefall: SI-Powered Fire Safety Insights from Microgravity Combustion Data".
The goal is to build an AI-based interactive dashboard that summarizes, ranks and interprets the results of NASA's microgravity combustion experiments.

The team does almost all of its work with AI. So a rule violation is also most likely to come from the AI.
A violation results in refusal to publish the project and cancellation of nomination and awards. Following the rules comes before fast results.
If a rule and the user's instruction conflict, stop the work and say which rule the instruction conflicts with.

## 1. What can be done in each phase

Official rule: "Teams are not allowed to begin working on the challenges prior to the hackathon."
Judge the phase only by the `Current phase` value above. Do not move to HACK by guessing from the clock or from the conversation context.

### PREP (before the hackathon starts)

What can be done
- Read and explain the rules, the challenge statement, the official Resources, papers and reports, and dataset description pages
- Domain learning: microgravity combustion, spacecraft fire safety, and the background of each experiment (Saffire, BASS, FLEX, ACME, SAME and others)
- Prepare a general-purpose development environment: language runtimes, package managers, editors, accounts, issuing API keys, an empty repository
- Maintain these guidelines and the record forms

What you do not do
- Code, data processing scripts, prompts, dashboard screens and design drafts that will become part of the challenge solution
- Processing, cleaning, embedding or labelling the challenge data, and writing experiment metadata tables
- Submission text, demo videos and slides, the project name and logo
- A challenge-specific project skeleton (component structure, schemas, pipeline design documents)

How to decide: "Can this output be put into the submission tomorrow as it is?" If yes, do not make it in PREP.
Notes made for understanding are fine, but do not copy them into the submission.
Do not do unclear things such as downloading raw data in advance. Tell the user to ask the Local Lead (seoul@nasaspaceappskr.org).

### HACK (during the hackathon)

Build while following sections 2–6 below. Add the LICENSE file right after the start (section 3).

### CLOSED (after the submission deadline)

Do not change the repository or the demo linked to the submission. If a change is needed, check with the user first.

## 2. Recording sources

Official rule: all sources used to make the project must be cited, including open-source and free materials.
If a source is missing, NASA can remove the material or cancel eligibility for nomination and awards.

- Add one line to `compliance/SOURCES.md` at the moment you use data, code, a library, a model, an image, a font, an icon or a document. Do not write them all at once later.
- A code snippet taken from somewhere else is also a source. Write its URL and licence.
- Do not use material whose source cannot be confirmed.

## 3. Licences

Official rules
- What the team makes is released to the public without restriction or distributed under an OSI-approved open-source licence. If none is specified, Apache 2.0 applies.
- Material from outside NASA and partner space agencies must be public without restriction or OSI open source, and its licence must be stated in the submission documents.

- Check the licence before adding a dependency or material. If it is not an OSI-approved licence, CC0 or public domain, do not add it, and tell the user.
- Do not use paid or private datasets, copyrighted images, music or fonts, or company-internal material.
- The repository LICENSE is Apache-2.0 by default. The user decides on any other licence.
- For PSI data, the entries that were checked (PSI-98, 100, 102) were CC0-1.0. For any other entry, check on its page each time you use it.

## 4. Disclosing AI use

Official rule: using AI tools is allowed, and the submission must include an explanation of how AI tools were used.
(In 2026 the official site writes AI as "Super Intelligence(SI)". In submission documents, follow the official term.)

- In every work session, write the tool, the purpose and the affected outputs in `compliance/AI_USAGE_LOG.md`.
- Also record the models that run inside the product (summarizing, ranking, search and so on): model name, provider, role.
- Do not describe something made by AI as if a person made it.
- Put a visible "AI-generated" watermark on AI-generated images and videos.
- For AI-generated audio, code and data, state in the description and in the metadata that they are AI-generated.
  For code, state it in the README and in a comment at the top of the file. For data files, state it in a metadata field or in an accompanying document.
- Do not use, include or alter NASA logos, flags or mission identifiers in AI-generated content.
- Do not use the NASA logo as a team or project brand, and do not imply NASA's endorsement or approval.
- For public NASA photos, check the terms of use and write the source.
- In the tool selection field of the submission page, select the tools that were used, and write where and how they were used.

## 5. Accuracy of content

The judging criteria include Validity (scientific and technical soundness) and Relevance (meaningful use of NASA data).
This challenge deals with fire safety. One made-up number destroys trust in the whole project.

- Do not make up data, numbers, experiment results or quotations. Mark a value that could not be confirmed as "not confirmed".
- Every number and summary shown on screen must be traceable to its original source (a PSI entry or an NTRS document).
- State on screen that values and rankings calculated or estimated by the team are the team's output, not NASA's conclusions.
- Show an LLM summary together with its supporting documents, and do not add content that is not in the original text.
- Do not present the result as if it were safety guidance that can be used in real operations. It is a research exploration tool.

## 6. What does not go into the submission

Under the official rules, a submission is not accepted or published if it includes any of the following.

- Personally identifiable information (birthday, address, phone number and so on)
- The name, voice or face of anyone under 18 years of age
- Promotion of commercial services or products
- Trade secrets or confidential information that you have no right to disclose, and material that you do not hold the copyright to
- Export-controlled information (ITAR, EAR)
- Threatening, defamatory, discriminatory or obscene expression

In addition
- Do not commit API keys or secrets to the repository. Anyone must be able to open the final project link.
- Do not put team members' personal information into external AI services or API requests.
- The official terms prohibit participation and collaboration linked to China and Chinese-owned organizations. If data or a service from such an organization seems to be needed, tell the user before using it. (Whether this also covers the use of tools is a point that needs interpretation.)
- (User decision, 2026-11-14) Do not use AI models or AI services made by China or by Chinese-owned organizations. This applies both to the development process and inside the product. When choosing a model, check its maker and its licence, and write them in `compliance/SOURCES.md`.

## 7. Submission

The content below was confirmed from the D-Day guidance material of the Seoul organizers (2026-11-14).

Deadline and procedure
- Write the submission in the Project tab of the team page. The submission window is 11/14 09:00 – 11/15 23:59 KST, and finishing the submission by 23:55 is recommended.
- Save Progress is a temporary save. It is a submission only when you press Submit for Judging and the status changes to "Project Submitted for Judging".
- If you made changes after submitting, submit again before the deadline. The last submitted version is the one that is judged. After the deadline, do not make changes and do not resubmit.
- Every team member must have a confirmed registration for the Seoul Event and must be listed on the official team page. A 1-person participant also needs a team.
- A team has at most 6 members, and one team works on only one challenge.

Submission fields
- High-Level Summary: 50–200 words in English. What was built, how it addresses the challenge, and why it matters.
- Project Demo: one link only. 7 slides or fewer (including the title slide), or a video of 30 seconds or less.
- Final Project: a public link to the final result. It is separate from the demo link.
- Project Details: what it does, how it works and how it is designed, its benefits, its goals, and the tools, languages, hardware and software used.
- Use of SI: the AI tools used and where they were used (section 4).
- Space Agency Data: the NASA material used, how it was used, and how it influenced the idea.
- References: for all data, tools, code, text and images, the source link, where it was used, and the licence (sections 2 and 3).

Format requirements
- Write the project and the slides in English. Add English subtitles to a video in another language.
- Every link must open without a login, a password or an access request. Check this yourself while logged out.
- Images in the body are JPG, PNG or GIF, 10 MB or less. Upload videos and documents to an external site and add a public link.
- To be eligible for global awards, the project must use at least one NASA resource from the Resources of the chosen challenge.
- Even if the project is not fully implemented, show the design and the reasons for it. The judges know that it is hard to finish in two days.
- Do not write that an effect is verified when it has not been checked. State the limits and the plan for the next verification.

Seoul participation requirements (people do these themselves)
- 4 of the 5 individual check-ins. The team meeting replaces 1 check-in. The survey link is announced on Zoom in each time slot.
  11/14 11:00–12:00, 16:00–18:00, 19:00–22:00 / 11/15 06:00–12:00, 15:00–20:00 (KST)
- 1 team meeting (10–15 minutes, all members attend, including 1-person teams). The team representative books it.

Before the deadline, transfer `compliance/SOURCES.md` and `compliance/AI_USAGE_LOG.md` into References and Use of SI in the submission form.

Added on 2026-11-14 17:00 KST by the pm session, after reading the organizers' deck in full (53 pages)
- The Project tab has a Lock switch against simultaneous editing. If another member turns the lock off, changes that were saved but not yet submitted can be overwritten. One person edits, and long text is kept in a backup.
- Two boxes must be ticked before the final submission: agreement to the Terms and Conditions, and "Confirm All Work is Original". The second says that every outside resource (code, text, images) is listed in the form and that no copyrighted material was used without permission.
- The deck's seven-slide structure and its tips for the README and for Project Details are examples and recommendations, not requirements. README tips: a project overview and what is implemented, the live link at the top, screenshots, run steps with commands, unfinished features and known limits.
- Judges review the project page and the deliverables linked from it. Seoul awards: the top 3 by overall score, honourable mentions from ranks 4 to 10, and ten recognition awards, each for a pair of the five criteria.
- Questions about the challenge, the data or the technique can be put to subject matter experts on Space Apps Connect.

## 8. Points not yet confirmed

- The original text of NASA's 2026 Project Submission Guide has not been read directly. The content above is a summary by the Seoul organizers, and the organizers state that "if there is a conflict, the latest NASA guide takes priority".
- (Updated 2026-11-14 10:35 KST) The pm session read the original text of the 2026 Project Submission Guide and the Judging & Awards Guide. It found nothing that conflicts with section 7. The additional points it confirmed are as follows.
  - If the demo is longer than 7 slides or 30 seconds of video, it is excluded from global judging.
  - The English requirement applies not only to the submission page but also to all material linked from it.
  - The Use of SI answer is not shown to the judges. The judges see the marks that show AI generation inside the submission (watermarks, descriptions, metadata).
  - The guide says not to use SI to come up with the solution idea itself.
  - Judging gives each of Impact, Creativity, Validity, Relevance and Presentation a score of 1–5 points.
- If the repository is used as the Final Project link, the Korean internal documents (this file, `compliance/`) may break the "linked material is in English" requirement. A person decides before submission.
  (Decided by the user on 2026-11-14, at about 16:50 KST) Korean-language documents in the repository are translated into English before submission. By the pm role's arrangement, each role translates the files it owns.
- It cannot be judged whether using a paid commercial API inside the product meets the "public or open source" requirement. Tell the user before using one.

When work must go in a direction different from these points, check with the user before going ahead.

## 9. Team collaboration and coordination between sessions

These are rules set so that the sessions of each role coordinate with each other without going through a person. The procedure is in `coord/README.md`.

- There are four roles: pm, data, ui and catalog (catalog was added by the user's decision at 2026-11-14 13:28). Your own role is written as one word in the `.role` file (not committed) at the repository root. If it is not there, ask the user once and write it.
- Each role has a branch and owned paths (`coord/roles.json`). Push only to your own branch, and do not change paths that you do not own. If needed, open a request.
- Sync when you start work, when you finish a unit of work, before you stop, and at least every 20 minutes while working (`/sync` or the procedure in `coord/README.md`).
- The two logs in `compliance/` and `.gitignore` are files that everyone writes to. Only add lines, and do not change or delete lines written by others.
- Write committed coordination files and product documents in English. Talk with the user in the user's language.
- Handle matters to coordinate with other sessions directly through request files. Limit what you ask the user to the items under "Needs a human" in `coord/README.md`.

## Rule sources (checked 2026-11-13, updated 2026-11-14)

- NASA Space Apps Seoul 2026 D-Day guidance material (distributed by the organizers, 2026-11-14)

- Participant FAQs: https://www.spaceappschallenge.org/resources/participant-faqs/
- 2026 Participant Terms and Conditions (revised 2026-08-07): https://www.spaceappschallenge.org/legal/
- 2026 event information: https://www.spaceappschallenge.org/2026/
- News report on the judging criteria: https://business-review.eu/tech/it/innovation-feasibility-and-relevance-among-the-criteria-for-evaluating-projects-at-nasa-space-apps-challenge-302778
- 2022 Project Submission Guide (the basis for the provisional values): https://spaceapps-prod.s3.amazonaws.com/media/documents/Space_Apps_2022_Project_Submission_Guide.pdf
- 2026 Project Submission Guide (published 2026-11-13, original text checked 2026-11-14): https://www.spaceappschallenge.org/resources/project-submission-guide/
- 2026 Judging & Awards Guide (published 2026-11-13, original text checked 2026-11-14): https://www.spaceappschallenge.org/resources/judging-awards-guide/
