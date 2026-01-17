# Data Visualization Components: SponsorScope.ai

**Role:** Autonomous Data Visualization Designer
**Objective:** Visualize uncertainty and ranges rather than precise, potentially misleading points.

## 1. Design Philosophy

*   **Fuzziness is Truth:** Precise lines imply certainty that doesn't exist. We use gradients and blurred edges to represent probability distributions.
*   **Neutrality:** Colors must not imply "Good" or "Bad" unless a critical safety threshold is breached.
*   **Accessibility:** High contrast for text, distinguishable shapes for colorblind users.

## 2. Color Tokens (Neutral Palette)

| Token Name | Hex Code | Usage |
| :--- | :--- | :--- |
| `color-viz-primary` | `#60a5fa` (Blue 400) | Main signal data. |
| `color-viz-range-fill` | `rgba(96, 165, 250, 0.2)` | The uncertainty band area. |
| `color-viz-range-stroke` | `rgba(96, 165, 250, 0.5)` | The edges of the band. |
| `color-viz-baseline` | `#475569` (Slate 600) | Background tracks / empty states. |
| `color-viz-warning` | `#facc15` (Yellow 400) | Low confidence / high variance. |
| `color-viz-critical` | `#a855f7` (Purple 500) | Statistical anomalies (not "errors"). |

## 3. Component Specifications

### 3.1 `<UncertaintyBand />`
Visualizes a value as a probability distribution range.

*   **Props:**
    *   `score` (number): The median/calculated value (0-100).
    *   `confidence` (number): 0.0 to 1.0. Lower confidence = wider band.
    *   `label` (string): Optional label (e.g., "Authenticity").
*   **Visual Logic:**
    *   `Range Width = (1 - confidence) * Multiplier`
    *   The "bar" is not a solid block but a gradient fading out at the edges.
    *   A thin vertical tick marks the median score.

### 3.2 `<ConfidenceMeter />`
A small, non-intrusive indicator of data reliability.

*   **Props:**
    *   `level` (number): 0.0 to 1.0.
*   **Visual Logic:**
    *   Signal bars (like cellular reception) or a simple text pill.
    *   If `level < 0.5`: Display warning icon.

### 3.3 `<SignalStrengthBar />`
For secondary metrics where ranges are overkill.

*   **Props:**
    *   `value` (number): 0-100.
    *   `threshold` (number): Optional benchmark.
*   **Visual Logic:**
    *   Simple slate-colored track.
    *   Primary color fill.
    *   Small marker for the benchmark.

## 4. Accessibility Notes

*   **Screen Readers:** All components must calculate and expose `aria-valuenow`, `aria-valuemin`, and `aria-valuemax`.
*   **Description:** Use `aria-label` to describe the range, e.g., "Estimated score between 60 and 80 percent."
*   **Contrast:** Ensure text labels against the slate background meet WCAG AA standards.
