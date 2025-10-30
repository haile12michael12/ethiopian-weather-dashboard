# Weather Dashboard - Design Guidelines

## Design Approach
**System Selected**: Material Design 3 principles with modern dashboard patterns
**Justification**: Information-dense weather application requiring clear data hierarchy, consistent dark/light mode implementation, and established patterns for charts and cards. Material Design provides robust guidelines for data visualization and responsive grids.

## Core Design Elements

### A. Color Palette

**Light Mode:**
- Background: 240 10% 98% (soft cool gray)
- Surface: 0 0% 100% (pure white cards)
- Primary: 210 100% 50% (sky blue - weather appropriate)
- Text Primary: 220 20% 15%
- Text Secondary: 220 15% 45%
- Border: 220 15% 90%

**Dark Mode:**
- Background: 220 20% 8% (deep charcoal)
- Surface: 220 18% 12% (elevated cards)
- Primary: 210 100% 60% (lighter sky blue for contrast)
- Text Primary: 220 10% 95%
- Text Secondary: 220 10% 70%
- Border: 220 15% 20%

**Accent Colors:**
- Success/Sunny: 45 100% 50% (warm amber)
- Alert/Cloudy: 220 15% 60% (muted slate)
- Warning/Rainy: 210 80% 45% (deep blue)

### B. Typography
**Font Stack**: Inter (via Google Fonts CDN)

- **Display/Headers**: 600 weight, 2rem-3rem (dashboard title)
- **Subheadings**: 500 weight, 1.25rem-1.5rem (card titles, section headers)
- **Body**: 400 weight, 0.875rem-1rem (stats, descriptions)
- **Data/Numbers**: 600 weight, 1.5rem-3rem (temperature displays)
- **Labels**: 500 weight, 0.75rem (chart axes, metadata)

### C. Layout System
**Spacing Primitives**: Tailwind units of 2, 4, 6, 8, 12, 16
- Component padding: p-4 to p-6
- Card gaps: gap-4 to gap-6
- Section spacing: py-8 to py-12
- Container max-width: max-w-7xl

**Grid System**:
- Dashboard container: grid with responsive columns
- Desktop: 3-column layout (current weather spanning 2 cols, stats 1 col)
- Tablet: 2-column layout
- Mobile: Single column stack

### D. Component Library

**Header Component**:
- Fixed top bar with shadow/blur backdrop
- Left: App title "🌍 Weather Dashboard" with gradient text effect
- Center: Search input with rounded-full styling, icon prefix
- Right: Dark/light mode toggle (sun/moon icons)
- Height: h-16
- Glassmorphism: backdrop-blur-md with semi-transparent background

**Current Weather Card**:
- Large card (col-span-2 on desktop)
- Top section: City name (text-3xl), timestamp
- Center: Massive temperature display (text-6xl font-bold) with animated counter
- Weather icon: Large emoji or icon (text-5xl)
- Bottom: Condition description, feels-like temperature
- Gradient background based on weather condition (sunny = warm gradient, rainy = cool gradient)
- Border radius: rounded-2xl
- Padding: p-8

**Stats Grid**:
- 5-6 mini cards in grid (grid-cols-2 md:grid-cols-3)
- Each card: icon, label, value, unit
- Icons from Heroicons (cloud, wind, droplet, eye, gauge)
- Compact padding: p-4
- Subtle hover effect: scale-105 transition
- Border radius: rounded-xl

**Charts Section**:
- Two chart cards side by side (responsive stack on mobile)
- Line chart: Temperature trend over 7 days
- Bar chart: Humidity levels
- Recharts styling: Primary color strokes, grid lines matching border color
- Chart height: h-64 to h-80
- Card padding: p-6
- Title above each chart (text-lg font-semibold)

**Map View (Optional Placeholder)**:
- Full-width card below charts
- Height: h-96
- Placeholder text centered if no map integration
- Border: dashed border for placeholder state

**Loading States**:
- Skeleton loaders matching card shapes
- Pulse animation (animate-pulse)
- Gradient shimmer effect for premium feel

**Footer**:
- Centered text: "Built with ❤️ using React + FastAPI"
- Subtle text color (text-secondary)
- Small padding: py-6

### E. Animations

**Framer Motion Patterns** (minimal, purposeful):
- **Initial Load**: Cards fade in with staggered delays (0.1s intervals)
- **Temperature Counter**: Animated number counting up on data refresh
- **Hover States**: Subtle scale (1.02) and shadow elevation on cards
- **Chart Transitions**: Smooth line/bar animations on data update (duration: 1s)
- **Mode Toggle**: Icon rotation (180deg) when switching dark/light
- **Loading State**: Gentle pulse, no aggressive spinning

**Interaction Feedback**:
- Search input: Focus ring with primary color
- Buttons: Hover brightness adjustment (hover:brightness-110)
- Cards: Hover shadow increase (hover:shadow-xl)

## Visual Effects

**Glassmorphism Application**:
- Header bar: backdrop-blur-md bg-white/80 dark:bg-slate-900/80
- Current weather card: Subtle backdrop-blur-sm on gradient backgrounds
- DO NOT overuse - only on header and hero weather card

**Shadows**:
- Cards: shadow-md default, shadow-xl on hover
- Header: shadow-sm for subtle depth
- Dark mode: Reduce shadow opacity by 50%

**Borders**:
- All cards: border border-color for definition
- Dark mode borders: Slightly lighter than background for visibility
- Input fields: 2px border on focus with primary color

## Responsive Behavior

**Breakpoints**:
- Mobile (<768px): Single column, stacked cards, full-width search
- Tablet (768px-1024px): 2-column grid, side-by-side charts
- Desktop (>1024px): 3-column layout, header stays compact

**Touch Targets**: Minimum 44px height for all interactive elements

## Data Visualization Specifics

**Chart Color Coding**:
- Temperature line: Primary color (sky blue)
- Humidity bars: Accent color (amber for high, blue for low)
- Grid lines: Border color for consistency
- Tooltips: Surface color with shadow, dark mode aware

**Icons Usage**:
- Heroicons for all UI icons (solid variant for active states, outline for default)
- Weather condition icons: Unicode emojis (☀️ ☁️ 🌧️ ⛈️ 🌤️) for simplicity
- Icon sizing: 20px (w-5 h-5) for UI, 40px+ for weather display

## Ethiopian Context Considerations
- Temperature display: Default Celsius, toggle for Fahrenheit
- City names: Proper Ethiopian city formatting (Addis Ababa, Dire Dawa, etc.)
- Date format: International standard (YYYY-MM-DD) with clear labels

## Accessibility
- Consistent dark mode across ALL elements including inputs
- Form inputs maintain readable contrast in both modes
- Icons paired with text labels for screen readers
- Focus indicators visible in both color schemes
- Minimum contrast ratio 4.5:1 for text