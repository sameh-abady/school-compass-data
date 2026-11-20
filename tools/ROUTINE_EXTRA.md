# Extra steps for the routines (3rd grader's study hub)

These steps are part of the routine. Do them inside step 2 (email sweep) and step 4 (update the JSON).
All text fields are bilingual `{"ar":"…","en":"…"}` (Arabic = Egyptian). The data lives in `D.study`:
`{tests:[…], weeks:[…], pattern:[…], focus:[…], spellLists:[…]}`. Create missing keys; never delete or reorder
`D.study.tests` (parents' locally typed scores are keyed by date + subject + title).

## A. Photos the parents email to themselves
Search (same window as the sweep): mail sent by either parent (`from:me`, or the other parent's address already
present in the artifact contacts) with `has:attachment` and a subject or body containing the 3rd grader's first name
together with `test`, `spelling` or `paper`, or the Arabic words `اختبار`, `كلمات`, `ورقة`.
Download every image/PDF attachment and read the image itself.

1. **Spelling word list** (a sheet of words, usually comes home Monday):
   - set `D.spelling = {week:{ar,en}, test:"YYYY-MM-DD", words:[…]}` — words exactly as printed, lower-case unless a
     proper noun. `test` = the date the newsletter gives; otherwise the Friday of that week.
   - append `{w:"<Monday YYYY-MM-DD>", test, words}` to `D.study.spellLists` (replace the entry with the same `w`).
2. **Test / quiz paper** (any subject):
   - subject key: `spelling | religion | math | reading | writing | science | social | fast | other`.
   - if `D.study.tests` already has an entry for the same subject within 3 days and it has no score, fill that entry in
     place; otherwise append `{d, subj, t:{ar,en}, score:"17", max:"20", missed:[…], note:{ar,en}}`.
   - `missed`: short items she got wrong — for spelling the correct words; for math the fact or skill
     (e.g. `"7×8"`, `{"ar":"مسائل كلامية","en":"word problems"}`); for others a 2–5 word bilingual phrase.
   - If the score or handwriting is unclear, still add it and set `"check": true`. Never guess a score: leave
     `score` null and say so in `note`.
   - Never store the image itself.

## B. From every new 3rd-grade weekly newsletter (read the image attachment)
- append/replace in `D.study.weeks` the entry for that week:
  `{w:"<Monday of 'Week of …'>", read, rel, sci, math, spell, tests?}` (one short bilingual line each).
- every test/quiz it announces → an entry in `D.study.tests` with `score:null, max:null, missed:[]`
  (skip if one exists for that subject and date) and an event for the 3rd grader (k "s") on that date.
- replace `D.study.focus` with what the class is working on now: `[{subj, t:{ar,en}}]` (3–5 rows).
- if it changes how the class runs (new routine, new testing day), edit the matching line in `D.study.pattern`.

## C. Report cards, FAST results, grades emailed by the school
- add rows to `D.grades` `[{k:"s", term:{ar,en}, subj:{ar,en}, mark}]` and, for a single test result, also to
  `D.study.tests`. Add an alert `{d, t, m}` saying the report is in.

## D. Monthly tuition (Blackbaud Tuition Management emails)
`D.tuition = {auto:{ar,en}, paid:[{d, a:"$1,264.25", m:{ar,en}}] (newest first), next:{d, a|null, m:{ar,en}}}`.
- "Automatic Payment Reminder" (arrives about a week before the 1st): set `next` = `{d:<debit date>, a:<payment due>,
  m:<one-line breakdown per student + fees>}` and add/update the family event on that date.
- "Your Automatic Payment Is Being Processed": move `next` into `paid` (use the posted date and the amount from the
  last reminder), append the same amount to `D.expenses` as `{d, k:"all", t:{ar,en}, a, cat:"fees"}` (skip if that
  date is already there), then set `next` to the 1st of the following month with `a:null`.
- A failed/declined payment or a past-due amount other than $0.00 → add an alert and a followup.
- Never store card or account numbers (not even the last four digits).

## E. Report cards (`D.reportCards`) — keep as is
`D.reportCards.{s|n}` (title, scale, terms, att, sections[{name, rows[{t, m[]}]}], comments) is entered by hand from
the school portal. Never delete or rewrite it. If the parents email a photo of a new term's report card, append the new
term to `terms`, push its mark onto each row's `m` (use "" when blank), add the comment, and update `D.study.rcWeak`
with the standards marked 1 or 2 in the newest term.
