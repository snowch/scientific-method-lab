# Research workspace redesign brief

Requested after the first published design was rejected as ugly. Apply the UX
and learning-design skills before choosing controls and after browser checks.
The Sites presentation-led guidance informs the course overview: concrete
examples and a useful next step, without repeated promotional sections.

Inspected the rendered overview, lesson and phone layout, and the page generator,
styles and interaction code. The previous visual hierarchy depended on oversized
serif headings, tiny utility text, a long single-column course listing and large
stretches of prose before a plain editor. Existing behaviour remains important:
local drafts, real execution, separate worked output, provenance and exports.

## Direction

A contemporary research workspace. Sora headings, DM Sans text, cool neutral
surfaces, deep ink, blue action colour and a dark Python editor. Use an explicit
spacing and type scale. Avoid ornamental typography and decorative novelty.

- Overview: one concise introduction, an interactive comparison using the
  invented equal-mean datasets from lesson 11, and six module panels in a compact
  two-column course map. Every investigation stays independently discoverable.
- Lesson: clear numbered stages, a narrower reading measure, visible learning
  outcome, compact prediction prompt and connected editor/result panels.
- Editor: syntax-coloured Python with line numbers, a real native textarea for
  editing and assistive technology, nearby Run/Stop and honest output states.
- Navigation: clear active lesson and a working course menu on mobile, with
  keyboard escape and focus recovery. Preserve existing URLs and saved work.

The comparison deliberately labels invented data. Switching between means and
individual readings changes a representation; it does not execute Python or
collect observations. Its purpose is to show the information a mean can hide.

## Checks

Inspect actual desktop and phone screenshots in light and dark themes. Test the
comparison toggle, keyboard controls, mobile menu, editor highlight/scroll sync,
restored drafts, loading/error/Stop recovery and exports. Run the full existing
course checks. Record findings and screenshots in docs/review.md. These checks
establish implementation behaviour, not observed learning effectiveness.
