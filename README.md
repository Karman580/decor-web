# Adorna Decor — website

`index.html` is the website. It began as an implementation of the
`ADH Decor.dc.html` design and has since been revised for the Adorna Decor
brand and indoor+outdoor positioning. One
self-contained file: no build step, no dependencies. Open it, or serve the
folder (`python3 -m http.server`) and visit it.

## Before launch

1. **Contact details.** `CONFIG` at the top of the `<script>` in `index.html`
   holds the WhatsApp number, phone, email and service area — all still
   placeholders.
2. **Google Form backend.** `FORM` is empty, so enquiries are not being recorded
   yet — see below. The form still validates and hands off to WhatsApp until you
   fill it in.
3. **Testimonials** are hidden. The `<section class="quotes" hidden>` markup is
   still in place with a comment explaining how to publish it — no invented
   reviews go live. Remove `hidden` once real feedback exists.
4. **Indoor imagery.** The portfolio `Indoor` filter has only one photograph.
   More indoor work would strengthen the brand's central claim; `check.py`
   prints the per-filter counts.

## Google Form backend

Enquiries are POSTed to a Google Form; its responses land in a Google Sheet you
can download as Excel. Nothing to host. Setup, once:

1. **Create the form** at [forms.new](https://forms.new). Add one question per
   field, in any order:

   `Name` · `Phone / WhatsApp` · `Email` · `Event Type` · `Indoor / Outdoor` ·
   `Location` · `Event Date` · `Number of Guests` · `Approximate Budget` ·
   `Tell Us About Your Vision`

   Three rules, all of which matter:
   - Make every question **Short answer** — including Event Date and Number of
     Guests. Date and multiple-choice types expect multi-part or exactly-matching
     values and will silently reject a plain POST. Use **Paragraph** for Vision.
   - Leave every question **not required**. Most site fields are optional, and a
     POST missing a required answer is rejected outright.
   - Add no response validation.

2. **Get the entry ids.** In the form editor, **⋮ → Get pre-filled link**, type a
   recognisable value into every field, then **Get link**. The link it copies
   contains an `entry.NNNNNNNNN=yourvalue` pair for each question — that is the
   id for that field.

3. **Get the action URL.** **Send → 🔗**, copy the link, and change the trailing
   `viewform` to `formResponse`.

4. **Paste both into `FORM`** in `index.html` — `action`, then each
   `entries.<field>`. Any field you leave `""` simply is not sent.

5. **Link the Sheet.** Form → **Responses** → the Sheets icon → *Create new
   spreadsheet*. Every submission appends a row, timestamped automatically.

6. **Export to Excel** whenever you want: in the Sheet, **File → Download →
   Microsoft Excel (.xlsx)**. Or open it in Excel via OneDrive to keep it live.

7. **Do one test submit on the site and check the Sheet.** This step is not
   optional — see the caveat below.

### Caveats

- **A wrong entry id fails silently.** Google Forms sends no CORS headers, so the
  browser cannot read the response; the page can tell that the request went out
  but not that Google accepted it. If an id is wrong the row is simply dropped
  and the visitor still sees the thank-you panel. Hence the test submit.
- **If the request cannot go out at all** (offline, blocked), the thank-you panel
  says so and points the visitor at WhatsApp, rather than implying a lost
  enquiry was received.
- **Inspiration photos cannot go through this.** Google Forms file uploads
  require the respondent to be signed in to Google and cannot be driven by a
  cross-origin POST. The field stays honest about sending them via WhatsApp.
- If you later want delivery confirmation, or real file uploads, a **Google Apps
  Script web app** (`doPost` appending to the Sheet) replaces `sendToGoogleForm`
  and can return proper CORS headers. More setup; only worth it for those two
  things.

## WhatsApp handoff

WhatsApp stays the prominent contact route regardless of the backend. A valid submission also loads the enquiry into a
prefilled WhatsApp message, so the visitor can send it directly.

The inspiration-photos field is real and reports what the visitor picked, but
both the form note and the thank-you panel say plainly that the files have to be
attached in the WhatsApp chat.

## Checks

- `python3 check.py` — static: every script id resolves, every filter selects at
  least one photograph, every `data-cfg` key is handled, every image path exists.
  Also prints the per-filter photo counts.
- `check-ui.html` — served alongside the site and opened in a browser, drives the
  real page in an iframe: filtering, lightbox navigation within a filter, form
  validation, the WhatsApp payload, and the Google Form POST (field→entry
  mapping, success and failure paths, with `fetch` stubbed so no network is
  touched). 30 assertions, all should read PASS.

## Photos

`uploads/` holds the eight event photographs plus `before-after-room.png`, the
supplied before/after diptych used as-is in the "From Any Space to Something
Special" section. Swapping any of them is a file replacement — no code change —
as long as the filename stays the same. `python3 check.py` fails loudly if a
reference ever points at a missing file.

Portfolio categories live in each shot's `data-cats` attribute, space separated,
first one being the label shown in the caption and lightbox. A photograph can
sit in several filters at once.

## Files

| | |
|---|---|
| `index.html` | the website |
| `check.py` | static wiring check — ids, filters, config bindings, image paths |
| `check-ui.html` | interaction check — filtering, lightbox, form, Google Form POST |
| `uploads/` | the eight event photographs + the before/after diptych |
| `ADH Decor.dc.html` | the imported design, source of truth for the look |
| `support.js`, `image-slot.js`, `_ds/` | Claude Design canvas runtime; only the `.dc.html` uses these |
