# zw-blog Design System

Source of truth for visual implementation. Page files in `design-system/pages/` override this file.

## Product

Personal reading log for technical notes and short reflections. Chinese first. No newsletter, no subscriber count.

## Color

| Token | Hex | Use |
| --- | --- | --- |
| `--ground` | `#DDE3EA` | Page background |
| `--ink` | `#16202C` | Headings and body |
| `--mute` | `#4E5D6C` | Meta, secondary nav |
| `--copper` | `#B85C38` | Bookmark rule, current nav, primary button |
| `--card` | `#F3F6F8` | Panels, comments, editor |
| `--rule` | `#C5CED6` | Dividers |
| `--code-bg` | `#16202C` | Code blocks |
| `--code-fg` | `#D7E3C8` | Code text |

Do not introduce a second accent.

## Typography

- Display: `Noto Serif SC`
- Body / UI: `IBM Plex Sans`, `Noto Sans SC`
- Mono / spine dates: `IBM Plex Mono`
- Article measure: max 62ch
- Body size: 17–18px, line-height 1.7

## Signature

A 2px copper vertical rule along the reading column, with a sideways (vertical) publish date like a book spine. Nothing else should compete with it.

## Motion

150–300ms color/opacity only. No scale on hover. Honor `prefers-reduced-motion`.

## Copy

Chinese. Sentence-case buttons. Exact strings live in `docs/05-ui-prototype.md` section 4.

## Anti-patterns

- Emoji as icons
- Placeholder-only inputs
- Full-bleed article text
- Pink subscribe CTA, handwritten English display fonts, warm-cream terracotta default
