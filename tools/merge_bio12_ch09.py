#!/usr/bin/env python3
"""Merge bio12-ch09 notes + MCQ links into notes.json / note_links.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from note_pipeline import (
    ROOT,
    build_links,
    load_bank,
    verify_all,
    print_distribution,
)

CHAPTER = {
    "id": "bio12-ch09",
    "class": 12,
    "chapterNo": 9,
    "title": "Strategies for Enhancement in Food Production",
    "topic": "Strategies for Enhancement in Food Production",
    "intro": "NCERT Class XII Unit VI Chapter 9: plant breeding and tissue culture, single cell protein and biofortification, and animal husbandry — dairy, poultry, apiculture, aquaculture and controlled breeding.",
    "default": "sfp-overview",
    "rules": [
        ("sfp-scp", r"single cell protein|\bscp\b|spirulina|methylophilus|fusarium|pruteen|mycelium.*protein|bacteria.*protein.*food|algae.*protein|yeast.*protein.*food|alga which can be employed as food|employed as food for human|organism can be used as food"),
        ("sfp-biofortification", r"biofortification|bio.?fortif|golden rice|vitamin.?a.*rice|iron.?rich|protein.?rich.*crop|micronutrient|malnutrition|fortified.*food|lysine and tryptophan|nutritional quality|diet deficiency.*iron|diet deficiency.*vitamin|iodine and zinc|essential amino acid.*crop|improved nutritional"),
        ("sfp-apiculture", r"apiculture|bee.?keep|bee.?keeping|honey bee|\bapis\b|bee.?wax|propolis|royal jelly|bee.?hive|beehives|bee hive|worker bee|honey is|honey contains|pollen.*bee|nectar"),
        ("sfp-aquaculture", r"aquaculture|pisciculture|fish culture|fish farming|catla|rohu|mrigal|hilsa|prawn|shrimp|marine water fish|freshwater fish|fisheries|fishery|fish.*rearing|fish is introduced|common carp|silver carp|grass carp|mackerel|gambusia|mosquito larva|larvicidal fish|marine fish.*omega|edible fishes"),
        ("sfp-dairy-poultry", r"dairy farm|dairy management|milch|milk.*yield|lactation|broiler|layer.*chicken|poultry|chicken.*infected|bird flu|avian flu|egg.*production|leghorn|rhode island|aisha|poultry farm|meat of.*chicken|properly cooked.*chicken"),
        ("sfp-animal-breeding", r"animal breeding|animal husbandry|livestock|moet|superovulation|embryo transfer|artificial insemination|\bai\b.*cattle|semen.*cattle|inbreeding|outbreeding|outcross|cross.?breed.*(cattle|sheep|goat)|interspecific hybrid|hissardale|\bmule\b|hinnie|controlled breeding|breed improvement|sahiwal|red sindhi|holstein|friesian|jersey|sheep.*cross|goat.*cross|bullock|bull.*docile|cloning of cattle|homozygous purelines.*cattle|animal cell culture|grain.*meat|kg of grain|eugenics|selective breeding.*human|sericulture|silkworm|silk.*product|genetic engineering|foreign gene|transgenic|superior by view of genotype"),
        ("sfp-heterosis", r"heterosis|hybrid vigou?r|f1 hybrid|single cross|double cross|triple cross|inbred line|line breeding|hybrid seed|p1542|hybrid variety"),
        ("sfp-tissue-culture", r"tissue culture|micro.?propagation|micropropagation|somaclone|somaclonal|callus|explant|anther culture|haploid|protoplast|embryo rescue|somatic hybrid|somatic embryo|meristem|shoot tip|virus.?free|cryopreserv|cellular totipotency|totipotenc|totipotency|pomato|in vitro clonal|clonal propagation|colchicine.*diploid|hormones.*culture.*tissue|artificial culture"),
        ("sfp-plant-breeding", r"plant breeding|green revolution|emasculation|bagging|cross.?pollinat|self.?pollinat|pure line|mutation breeding|germplasm|germ.?plasm|gene pool|collection.*allele|cultivar|hybridization|hybridis|selection.*breed|pusa|wheat|rice|maize|sugarcane|sorghum|mung|moong|rust|smut|resistance|variety|varieties|crop|yield|himgiri|sharbati|sonora|ir.?8|jaya|ratna|borlaug|swaminathan|brassica|saccharum|tobacco|cotton|mustard|sunflower|groundnut|gram|pulses|oilseed|plant hybrid|new genetic variety|breeding.*crop|pollination.*generation|sequential steps.*breed|priority of plant breeder|viability of seeds|seed bank|organic farming|causative agent.*disease|match.*column.*disease|testing.*release.*commercial|fungicide|fungal disease|bordeaux|downy mildew|black rot|xanthomonas|bacterial blight|incorrect match|wrong combination|iari|iucn"),
    ],
    "sections": [
        {
            "id": "sfp-overview",
            "level": 2,
            "heading": "1. Food production — overview",
            "html": "<p>With a growing human population, <strong>enhancement of food production</strong> is essential. Strategies include <strong>plant breeding</strong>, <strong>tissue culture</strong>, <strong>animal husbandry</strong> (dairy, poultry, fisheries, apiculture) and microbial foods (<strong>SCP</strong>). In India agriculture accounts for ~<strong>14% of GDP</strong> and employs ~<strong>50% of the population</strong>. Good breeds should be high-yielding, disease-resistant, tolerant to climatic stress and have better quality products. A shift from grain to meat diet increases cereal demand (~<strong>3–10 kg grain per kg meat</strong>).</p>",
        },
        {
            "id": "sfp-plant-breeding",
            "level": 2,
            "heading": "2. Plant breeding",
            "html": "<p><strong>Plant breeding</strong> manipulates plant species for superior crops. Steps: (i) collection of <strong>germplasm</strong> (entire collection of diverse alleles — the <strong>gene pool</strong>); (ii) evaluation and selection of parents; (iii) <strong>hybridization</strong> of selected parents; (iv) selection and testing of superior <strong>recombinants</strong>; (v) testing, release and <strong>commercialisation</strong> of new cultivars. <strong>Emasculation</strong> (removal of anthers) and <strong>bagging</strong> (covering emasculated flower) prevent unwanted pollination in cross-pollinated crops. Self-pollination for several generations yields <strong>pure lines</strong>. <strong>Mutation breeding</strong> uses physical/chemical mutagens. The <strong>Green Revolution</strong> (1960s–70s) — high-yielding, disease-resistant <strong>wheat and rice</strong> via plant breeding — was led globally by <strong>Norman Borlaug</strong> and in India by <strong>M. S. Swaminathan</strong>. Indian varieties: wheat (<strong>HL-21, Sonalika, Kalyan Sona</strong>); rice (<strong>IR-8, Jaya, Ratna</strong>); sugarcane (<em>Saccharum barberi</em> × <em>S. officinarum</em>); millets; <strong>Pusa</strong> varieties (e.g. <strong>Pusa Gaurav</strong> — mustard; <strong>Pusa Komal</strong> — cowpea; <strong>Pusa Sadabahar</strong> — chilli); <strong>Himgiri</strong> (wheat — leaf/stripe rust resistant).</p>",
        },
        {
            "id": "sfp-tissue-culture",
            "level": 2,
            "heading": "3. Tissue culture & micropropagation",
            "html": "<p><strong>Tissue culture</strong> regenerates whole plants from explants on nutrient medium under aseptic conditions. <strong>Totipotency</strong> — capacity of a cell to generate a whole plant. <strong>Micropropagation</strong> (clonal propagation) produces thousands of identical plants from shoot tips/meristems — virus-free plants (e.g. banana, potato, sugarcane). Steps: explant → <strong>callus</strong> → shoot/root induction → hardening → field transfer. <strong>Somaclonal variation</strong> — genetic variation among tissue-culture-derived plants. <strong>Anther culture</strong> → haploid plants; <strong>embryo rescue</strong> saves weak interspecific hybrids; <strong>protoplast fusion</strong> → somatic hybrids (e.g. <strong>Pomato</strong> = potato + tomato). <strong>Cryopreservation</strong> stores germplasm at −196 °C (liquid N₂). Hormones: <strong>auxin + cytokinin</strong> ratio controls organogenesis.</p>",
        },
        {
            "id": "sfp-heterosis",
            "level": 2,
            "heading": "4. Heterosis & hybrid seeds",
            "html": "<p><strong>Heterosis (hybrid vigour)</strong> — superior performance of <strong>F₁ hybrids</strong> over parents in yield, growth, uniformity and disease resistance. Commercial hybrid seed production: develop <strong>inbred lines</strong> by repeated self-pollination → cross two inbreds → <strong>single cross hybrid</strong>; <strong>double cross</strong> and <strong>triple cross</strong> hybrids use more parental lines for greater vigour but lower uniformity. Hybrid seeds must be purchased each season (F₂ segregates). Examples: maize, rice, sorghum hybrid varieties (e.g. <strong>P-1542</strong>).</p>",
        },
        {
            "id": "sfp-biofortification",
            "level": 2,
            "heading": "5. Biofortification",
            "html": "<p><strong>Biofortification</strong> breeds crops with higher levels of vitamins, minerals, proteins or healthier oils — sustainable remedy for <strong>hidden hunger</strong> (micronutrient deficiency: iron, vitamin A, iodine, zinc). Targets: <strong>protein quality</strong> (lysine, tryptophan in maize/wheat); <strong>micronutrients</strong> (iron, vitamin A); oil quality. Examples: <strong>Atlas 66</strong> (wheat, high protein); <strong>Golden rice</strong> (β-carotene / vitamin A precursor); iron-rich varieties. Distinct from fortification (adding nutrients during processing).</p>",
        },
        {
            "id": "sfp-scp",
            "level": 2,
            "heading": "6. Single cell protein (SCP)",
            "html": "<p><strong>Single cell protein (SCP)</strong> — microbial biomass (bacteria, yeasts, algae, filamentous fungi) grown on industrial/agricultural waste, harvested and used as food/rich protein supplement. Advantages: rapid biomass production, independent of land, uses waste substrates. Sources: <strong>Spirulina</strong> (alga, 60% protein, on wastewater); <strong>Methylophilus methylotrophus</strong> (bacterium, 43% protein, on methanol); <strong>Fusarium</strong> (fungus, <em>Pruteen</em>, on glucose); <strong>Candida utilis</strong> (yeast, on molasses). SCP can reduce pressure on agricultural land for protein.</p>",
        },
        {
            "id": "sfp-animal-breeding",
            "level": 2,
            "heading": "7. Animal breeding & husbandry",
            "html": "<p><strong>Animal husbandry</strong> — care and breeding of livestock (cattle, sheep, goat, poultry, pig) for food, fibre and labour. Breeding aims: increased milk/meat/egg production, disease resistance, quality. Methods: <strong>inbreeding</strong> (closely related animals — exposes harmful recessives, reduces fertility; used to develop pure lines); <strong>outbreeding</strong> — out-crossing (same breed, unrelated), cross-breeding (superior breeds, e.g. <strong>Hissardale</strong> = Bikaneri × Marino sheep), interspecific hybridization (<strong>mule</strong> = horse × donkey, sterile). <strong>MOET</strong> (Multiple Ovulation Embryo Transfer): FSH → superovulation → AI → non-surgical recovery at 8-cell stage → embryo transfer to surrogates — rapid multiplication of elite cows. <strong>Artificial insemination</strong> (AI) uses proven sire semen. Castrated bull → docile <strong>bullock</strong> for farm work.</p>",
        },
        {
            "id": "sfp-apiculture",
            "level": 2,
            "heading": "8. Apiculture (bee-keeping)",
            "html": "<p><strong>Apiculture</strong> — maintenance of honeybee hives for honey and wax. Species: <strong>Apis indica</strong> (common Indian), <strong>A. dorsata</strong> (rock bee), <strong>A. florae</strong> (little bee), <strong>A. mellifera</strong> (Italian, high yield). Products: <strong>honey</strong> (fructose/glucose, minerals, enzymes), <strong>bee wax</strong>, <strong>propolis</strong>, <strong>royal jelly</strong>. Bee-keeping needs: knowledge of nature/habits of bees, suitable location, catching/swarming, management during flowering. Hives in crop fields during flowering increase <strong>pollination</strong> and crop yield. Worker bees live ~6 weeks (busy season) to months (winter).</p>",
        },
        {
            "id": "sfp-aquaculture",
            "level": 2,
            "heading": "9. Fisheries & aquaculture",
            "html": "<p><strong>Fisheries</strong> — industry dealing with catching, processing and selling fish/shellfish. <strong>Aquaculture (pisciculture)</strong> — rearing fish in confined water bodies. Freshwater fishes: <strong>Catla</strong> (surface feeder), <strong>Rohu</strong> (column feeder), <strong>Mrigal</strong> (bottom feeder), common carp, grass carp, silver carp. Marine: <strong>Hilsa</strong>, pomfret, mackerel. Composite fish culture stocks 5–6 compatible species with different feeding niches for high yield without competition. <strong>Prawn/fish culture</strong> integrated with rice paddies in some systems. <strong>Common carp</strong> introduced to India by foreigners.</p>",
        },
        {
            "id": "sfp-dairy-poultry",
            "level": 2,
            "heading": "10. Dairy & poultry management",
            "html": "<p><strong>Dairy farm management</strong> — processes for improved milk yield and quality: selection of high-yielding <strong>milch breeds</strong> (<strong>Sahiwal, Red Sindhi</strong> — indigenous; <strong>Holstein-Friesian, Jersey</strong> — exotic; cross-breeds for hybrid vigour), proper housing, feeding, hygiene, veterinary care, <strong>AI</strong> with superior bulls, record-keeping. <strong>Poultry</strong> — domesticated fowl for eggs and meat. <strong>Broilers</strong> (meat, fast growth) and <strong>layers</strong> (egg production). Breeds: <strong>Leghorn, Rhode Island Red, Aseel (Aisha)</strong>. Management: breed selection, disease-free stock, balanced feed, hygiene, temperature control. Infected birds culled; <strong>bird flu</strong> not transmitted by properly cooked chicken/eggs (&gt;100 °C).</p>",
        },
    ],
}


def insert_after(chapters: list[dict], chapter: dict, after_id: str) -> None:
    chapters[:] = [c for c in chapters if c["id"] != chapter["id"]]
    for i, c in enumerate(chapters):
        if c["id"] == after_id:
            chapters.insert(i + 1, chapter)
            return
    chapters.append(chapter)


def main() -> None:
    notes = json.loads((ROOT / "notes.json").read_text(encoding="utf-8"))
    note_links = json.loads((ROOT / "note_links.json").read_text(encoding="utf-8"))

    ch = CHAPTER
    chapter_notes = {k: v for k, v in ch.items() if k not in ("default", "rules")}
    insert_after(notes["chapters"], chapter_notes, "bio12-ch08")

    questions = load_bank(ch["topic"])
    assert len(questions) == 229, f"expected 229 MCQs, got {len(questions)}"

    links = build_links(questions, ch["rules"], ch["default"])
    link_entry = {
        "id": ch["id"],
        "topic": ch["topic"],
        "linkCount": len(links),
        "links": links,
    }
    insert_after(note_links["chapters"], link_entry, "bio12-ch08")

    (ROOT / "notes.json").write_text(
        json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "note_links.json").write_text(
        json.dumps(note_links, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"Merged {ch['id']}: {len(questions)} MCQs → {len(links)} links")
    print_distribution(links)

    errs = verify_all()
    if errs:
        for e in errs:
            print(e)
        sys.exit(1)
    print("All linked chapters pass verification (0 missing, 0 orphan).")


if __name__ == "__main__":
    main()
