# Obsidian Aesthetic Library Skill

[中文](README.md)

A Codex Skill for building a design inspiration library in Obsidian. It combines studio subscriptions, a permanent project baseline, weekly updates, reading status, controlled tags, and editorial selections in a lightweight local workflow.

## What it builds

- A studio gallery for browsing and filtering the studios you follow.
- A project gallery searchable by branding, typography, visual identity, concepts, and other dimensions.
- A starter catalog of 52 studios with extensible source configuration.
- A permanent historical baseline and weekly synchronization, so old work is not mistaken for a new release.
- Read/unread management, controlled tags, AI editor notes, and a weekly selection.
- Folder-name-independent scripts for checking, repairing, and synchronizing the library.

## Automatic subscriptions and weekly updates

After initialization, the Skill creates source configuration and a permanent project baseline for each studio. It can collect from official project pages, feeds, sitemaps, or verified page-monitoring entry points, then compare the result with the baseline to identify genuinely new projects.

To run the workflow automatically each week, ask Codex to create a weekly task:

```text
Create a weekly automation for my aesthetic library: synchronize new projects from every studio, prepare the candidate queue, and generate the weekly selection.
```

Each weekly run can:

1. Check whether the configured sources are still valid.
2. Synchronize new projects and deduplicate them against the permanent baseline.
3. Build a candidate queue for the AI editor to add a Chinese introduction, tags, an observation focus, and a short editorial note.
4. Prepare the weekly selection: up to 15 projects for the first issue and up to 10 for later issues, with the actual count based on the quality of that week's additions.

A recurring task requires explicit user authorization and setup. Installing the Skill does not silently create a background schedule.

## Included studio catalog

The starter catalog contains 52 studios across branding, graphic design, typography, publishing, motion, digital experiences, spatial design, and experimental practice. It is an editable starting point; source availability reflects the audit date stored in the catalog.

### Global pilot

- [Pentagram](https://www.pentagram.com/): A partner-owned independent design consultancy spanning brand strategy, identity, publishing, digital experiences, motion, and spatial design.

### China

- [ABCD](https://ablackcover.com/): An international brand-led design studio creating strategy, identity, packaging, and communications for emerging brands and new retail.
- [Studio NA.EO](https://www.studionaeo.com/): An independent visual design studio working across brand identities, cultural events, exhibitions, and consumer projects.
- [RELATED](https://www.related.design/): A visual practice rooted in art and culture, with work across publications, posters, exhibition identities, records, and websites.
- [Pocca](https://pocca.design/): A research-driven studio connecting brand strategy with visual storytelling through information, facts, and emotion.
- [Same Paper](https://samepaper.com/): A Shanghai creative studio and independent product label focused on photography, publishing, and self-initiated products.
- [Workbyworks](https://workbyworks.studio/): A multidisciplinary New York and Shanghai studio providing creative direction, identity, packaging, web, and book design.
- [KAUKAU](https://www.kaukau.design/): A brand identity studio using typography, layout, packaging, and motion to build coherent visual systems.
- [Qingyu Wu](https://qingyuwu.com/): A design practice serving artists, musicians, brands, schools, and museums, with an emphasis on print and graphic identity.
- [HDU²³ Lab](https://hdu23lab.com/): A small Wuxi graphic design studio creating identities, posters, and packaging for retail, food, and internet projects.
- [Guawa Design](https://www.guawadesign.com/): A Shanghai and New York brand studio offering strategy, identity, campaigns, and visual consultancy for commercial and cultural clients.
- [Mint Design](https://mintdesign.cn/): A multidisciplinary studio exploring relationships among people, art, and function through observations of everyday life and place.

### Japan

- [GOO CHOKI PAR](https://gcp.design/): A Tokyo design and art collective of three graphic designers known for cross-language communication and experimental graphics.
- [Yuta Takahashi Design Studio](https://yutatakahashi.jp/): A studio solving brand problems through strategy, concept development, refined identities, and packaging systems.
- [TAKAIYAMA](https://takaiyama.jp/): A Tokyo art direction and graphic design studio working across print, books, logos, signage, and visual communication.
- [STUDIO DETAILS](https://www.details.co.jp/): A brand consultancy connecting value assessment and strategy with creative development, websites, products, and communications.
- [Semitransparent Design](https://www.semitransparentdesign.com/): A team of designers, device developers, and programmers exploring digital design and installations between networks and physical space.
- [Whatever](https://whatever.co/): A creative team spanning advertising, entertainment, and technology, from branding and film to products and new ventures.
- [UMA / design farm](https://beta.umamu.jp/): A practice addressing culture, welfare, and regional issues through graphics, spaces, exhibitions, and public-facing programs.
- [LABORATORIES](https://www.labor-atories.com/): A Tokyo studio centered on art direction and visual communication across graphics, books, websites, and signage.
- [we+](https://weplus.jp/): A contemporary design studio using research and experimentation to explore nature, society, and values overlooked by efficiency-driven systems.

### Europe

- [Studio Feixen](https://www.studiofeixen.ch/): A Swiss multidisciplinary studio extending visual concepts into graphic design, type, animation, products, and spaces.
- [Studio Yukiko](https://y-u-k-i-k-o.com/): A Berlin creative agency providing direction, visual development, brand strategy, and concepts for commercial and cultural clients.
- [Studio Nari](https://www.studionari.co.uk/): A culture-led brand studio building identities, experiences, and expressions that people can feel part of.
- [How&How](https://how.studio/): A London and Los Angeles agency combining strategy, design, and digital experiences to build recognizable brands.
- [Studio Kiln](https://www.studio-kiln.com/): A studio creating living brands through identity, storytelling, and digital experiences for culture, entertainment, and technology.
- [OMSE](https://www.omse.co/): An independent London studio building clear, meaningful brands that connect organizations with their audiences.
- [Studio Airport](https://www.studioairport.nl/): An interdisciplinary studio combining strategy and creativity through prototyping, storytelling, film, and experiential work.
- [Barkas](https://barkas.com/): An independent Copenhagen creative company building brands across identity, communications, and digital touchpoints.
- [Bielke&Yang](https://bielkeyang.com/): An Oslo agency focused on identity and long-term brand building, including websites, storytelling, and place-making.
- [Studio Mut](https://www.studiomut.com/): An Italian graphic design studio creating identities, digital platforms, and publications while exploring motion and exhibitions.
- [The Rodina](https://www.therodina.com/): An experimental practice between culture and technology using performance, games, and research to create visual and participatory environments.
- [Offshore Studio](https://www.offshorestudio.ch/): A Zurich and Vienna collaborative practice researching editorial design, typography, image-making, and visual narratives.
- [Badesaison](https://www.badesaison.ch/): A Zurich studio producing books, publications, posters, and identities, with extensions into web applications and spatial installations.
- [Marcus Kraft](https://www.marcuskraft.com/): A Zurich visual communication studio combining strong narratives and typography across branding, publishing, exhibitions, packaging, signage, and digital work.
- [Ohlman Consorti](https://www.ohlmanconsorti.com/): A Paris advertising and digital media consultancy specializing in art direction, imagery, typography, publishing, and websites.
- [Koto](https://koto.com/): An international brand studio combining strategy, co-creation, and detailed execution across brand touchpoints.

### North America

- [PORTO ROCHA](https://www.portorocha.com/): A New York and London strategy and design agency balancing rigor and emotion in major rebrands and independent cultural work.
- [Actual Source](https://actualsource.work/): A studio extending strategy, creative direction, and identity into publishing, websites, packaging, clothing, and physical spaces.
- [DIA Studio](https://www.dia.studio/): A design, research, and innovation studio focused on kinetic identities, typographic systems, and generative design tools.
- [Order](https://order.design/): A brand identity office emphasizing reasoned decisions, standards, archives, and systematic execution.
- [Center](https://center.design/): A Brooklyn brand team creating identity, packaging, strategy, motion, 3D, and web work for consumer brands.
- [Other Means](https://othermeans.us/): A Brooklyn graphic design studio serving cultural institutions through typographic identities, publishing, exhibitions, signage, and websites.
- [Sunday Afternoon](https://sundayafternoon.us/): A New York brand and artist-management agency combining strategy and identity with campaigns, typography, photography, motion, and film.
- [Wedge](https://www.wedge.work/): A Montreal and Los Angeles agency building distinctive brands, often in food, consumer goods, and lifestyle.
- [Caserne](https://www.caserne.com/): A Montreal studio organizing brands around story and purpose, from positioning and naming to complete visual systems.
- [Mouthwash Studio](https://mouthwash.studio/): A studio working across art, architecture, fashion, technology, and sustainability through strategy, visual design, motion, and digital experiences.
- [&Walsh](https://andwalsh.com/): A New York brand and advertising agency covering strategy, design, art direction, campaigns, social content, and final image production.
- [Special Offer](https://www.specialoffer.inc/): A creative technology company using digital experiences to connect technology, interaction design, and internet subcultures.
- [Gander](https://takeagander.com/): A New York branding and graphic design studio shaping characterful brands through strategy, packaging, websites, and art direction.
- [Polymode](https://www.polymode.studio/): A minority- and queer-owned studio serving cultural and social justice work through research, publishing, identity, exhibitions, and education.
- [Landscape](https://thisislandscape.com/): A multidisciplinary studio using brand strategy, design systems, and communications to support social, environmental, scientific, technological, and cultural change.

## Requirements

- Codex
- Obsidian with the Bases core plugin enabled
- Python 3

## Installation

Clone the repository into the Codex Skills directory:

```bash
git clone https://github.com/shawpeng8815/obsidian-aesthetic-library-skill.git ~/.codex/skills/obsidian-aesthetic-library-skill
```

Restart Codex, then invoke the Skill with a prompt such as:

```text
Use $obsidian-aesthetic-library-skill to build a design aesthetic library in my Obsidian Vault.
```

Codex will ask for the target path and whether to use the bundled 52-studio catalog or begin with an empty catalog.

## Notes

The repository contains reusable templates, scripts, field specifications, and the starter catalog. It does not include harvested project content or downloaded images. Studio websites, feeds, and page structures can change, so revalidate sources before production synchronization.

See [`SKILL.md`](SKILL.md) for the complete agent workflow.
