# Extra steps for the routines (3rd grader's study hub)

These steps are part of the routine. Do them inside step 2 (email sweep) and step 4 (update the JSON).
All text fields are bilingual `{"ar":"…","en":"…"}` (Arabic = Egyptian). The data lives in `D.study`:
`{tests:[…], weeks:[…], pattern:[…], focus:[…], spellLists:[…]}`. Create missing keys; never delete or reorder
`D.study.tests` (parents' locally typed scores are keyed by date + subject + title).

## 0. Every run stamps the check time
The page shows parents how long ago the data was checked, from `D.updated`. So on EVERY run — also when no email is
new and nothing else changed — set `D.updated` to the current time (America/Chicago ISO) and republish index.html
(then do step 7 as usual). A run that checked everything and found nothing must still move this time forward.

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

## E. Practice tests — three every week (`D.study.quizzes`)
The 3rd grader takes two practice tests a week inside the app: **Wednesday = language & reading** (`kind:"lang"`),
**Saturday = math & review** (`kind:"math"`). On every run make sure a quiz exists for the next Wednesday and the next
Saturday (America/Chicago); if one is missing, write it and append it. Never edit or delete a quiz whose date is today or
in the past (results are stored on the parents' phones by quiz id). Keep at most the newest 30 quizzes.

There is also a third weekly test: **Monday = the other subjects** (`kind:"other"`, id `YYYY-MM-DD-other`, title
`{ar:"امتحان باقي المواد: Science و Social Studies والدين", en:"Other subjects test: Science, Social Studies & Religion"}`).
Make sure one exists for the next Monday too. 16 `mc` questions: 6 `science`, 5 `social`, 5 `religion`, taken from what
class covered in the last weeks (`D.study.weeks` fields `sci` and `rel`, the study guides and the school papers) and
from `missed` items of religion/science tests. Facts only, one clearly right option, same Arabic guide fields.

Shape: `{id:"YYYY-MM-DD-lang|math", d:"YYYY-MM-DD", kind, title:{ar,en}, passage?:"…", q:[…]}` with 14–16 questions.
Question shapes (question text is English only, like the school's papers):
- multiple choice `{s, t:"mc", q:"…", o:["…","…","…","…"], a:<index of the right option 0–3>, why?:"one short sentence"}`
- number answer `{s:"math", t:"num", q:"7 × 8 = ?", a:"56"}` (word problems too; the answer is a bare number)
- spelling with audio `{s:"spelling", t:"spell", w:"playground"}`
`s` is one of `reading | vocab | word | grammar | math | spelling | religion | science | social`. Vary the position of the right option.

Content rules:
- Write ORIGINAL questions in the style of the school's "Progress Check-Up" sheets. Never copy questions or passages from
  school papers, textbooks or the web.
- Take the topics from the newest entries of `D.study.weeks` and `D.study.focus` (what class is doing now) and revisit what
  she missed: `missed` items in `D.study.tests` and the standards marked 2 in `D.reportCards.s`.
- **lang**: an original 90–130 word passage in `passage` + 6 `reading` questions (main idea, a detail with evidence,
  cause/effect, a word in context, sequence or inference, "which sentence shows…"), 4 `vocab` (synonym in a sentence —
  the unit's words), 4 `word` (contractions, compound words, plurals, vowel patterns — the current word-study skill),
  2 `grammar`. Reading comprehension is her weakest area: keep those questions careful and unambiguous.
- **math**: 6 facts (× and ÷, include a missing-number one), 3–4 word problems (one two-step), 1–2 on the current topic,
  3 `spell` words from `D.spelling.words` or the newest `D.study.spellLists`, 2 `religion` or `science` review questions.
- Every question must have exactly one correct answer; check each `a` before saving. Grade 3 level, no trick questions.

Arabic parent guide (the app shows and prints an Arabic copy so a parent can explain each answer) — required on every
new quiz:
- every question gets `qa` (the question in simple Egyptian Arabic; for `spell` the word's Arabic meaning) and `how`
  (2–4 short Arabic steps that solve it the way the school teaches it). `mc` questions also get `aa` (the right
  option's meaning in Arabic only). A `lang` quiz gets `passageAr` (the passage in Arabic).
- every question also gets `howEn`: the same steps as `how`, in the same order and the same number of items, in
  short simple English a third grader understands (the app reads them aloud in its interactive lesson and builds
  the animation from them). Write every equation in full with digits and the signs × ÷ + − = (`4 × 7 = 28`), list
  skip counting as numbers separated by commas (`7, 14, 21, 28`), quote passage evidence inside “ ”, write compound
  words as `rattle + snake`, and spell letters out with spaces (`silent g h`).
- write equations with Western digits and `?` for the unknown (`6 × ? = 54`), never an Arabic word inside an equation;
  keep school terms in English inside the Arabic (bar diagram, equation, fact family, skip counting, evidence).
- school method, math (enVision): equal groups; skip counting for facts; division through the related multiplication
  fact / fact family; word problems = bar diagram + equation with `?` + answer with its unit; two-step problems as
  "Step 1 … Step 2 …". One-step × or ÷ word problems also get
  `bar:{total:"54"|"?", n:<number of equal groups, max 12>, each:"6"|"?", tl:"muffins in all", el:"in each box"}`.
- school method, language: go back to the passage and underline the evidence sentence (quote it inside “ ”); vocabulary
  by context clues (try each option in the sentence); plurals, contractions and compound sentences by naming the rule.

## F. Word bank (all the words she has to learn)
- Every spelling list goes into `D.study.spellLists` as `{w, test, name:{ar,en}, words:[…]}` — `name` is the pattern
  (e.g. "Contractions", "Long vowels (VCe)"); include the challenge and high-frequency words printed on the sheet.
- Reading vocabulary goes into `D.study.vocab`: `[{name:"<story> (Unit N, wk N)", words:[{w, en:"short meaning", ar:"المعنى"}]}]`
  — append a group when a new story's vocabulary appears on a paper or in a newsletter. Never delete groups.

## G. Library holds already picked up (`D.libPicked`)

`D.libPicked` lists book titles the family has already picked up from the public library. Never add or keep a
"last day to pick up" event for a title in that list, even if an older hold email is still in the inbox. Keep the
"due back" event (src `lib`) until its date has passed; if a later library email gives a new due date for those
books (renewal), update that event's date.
