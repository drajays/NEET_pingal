#!/usr/bin/env python3
"""Merge bio12-ch01..ch04 notes + MCQ links into notes.json / note_links.json."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from note_pipeline import (  # noqa: E402
    build_links,
    load_bank,
    upsert_chapter_links,
    upsert_chapter_notes,
    verify_all,
)

CHAPTERS: list[dict] = [
    {
        "id": "bio12-ch01",
        "class": 12,
        "chapterNo": 1,
        "title": "Reproduction in Organisms",
        "topic": "Reproduction in Organisms",
        "intro": "NCERT Class XII Unit VI Chapter 1: why organisms reproduce, life spans, asexual modes (fission, budding, fragmentation, spores, vegetative propagation) and the essentials of sexual reproduction — meiosis, gametes, fertilisation, zygote formation, and reproductive strategies in plants and animals.",
        "sections": [
            {
                "id": "ro-overview",
                "level": 2,
                "heading": "1. Reproduction — why and how",
                "html": "<p><strong>Reproduction</strong> enables continuity of the species by producing progeny similar to parents. It is <strong>not a defining property of life</strong> (many organisms do not reproduce yet are living), but it is essential for species survival. Organisms reproduce by <strong>asexual</strong> (single parent, no gamete fusion) or <strong>sexual</strong> (two parents/gametes fuse) methods. <strong>Juvenile phase</strong> precedes reproductive maturity; <strong>senescence</strong> follows. Reproductive events are seasonal in many plants and animals (photoperiod-sensitive breeders).</p>",
            },
            {
                "id": "ro-lifespan",
                "level": 2,
                "heading": "2. Life span",
                "html": "<p>Every organism has a characteristic <strong>life span</strong> — the period from birth to natural death. It varies enormously: bacteria minutes to hours; insects days to weeks; rice ~1 year; butterfly ~1–2 weeks; crow ~15 years; dog ~10–13 years; cat ~15–20 years; elephant ~60–90 years; tortoise ~100–150 years; peepal/Banyan tree hundreds of years. Life span is not correlated with body size.</p>",
            },
            {
                "id": "ro-asexual",
                "level": 2,
                "heading": "3. Asexual reproduction",
                "html": "<p><strong>Asexual reproduction</strong> — offspring from a single parent without meiosis/fertilisation; progeny are <strong>genetically identical (clones)</strong>. Common modes:</p><ul><li><strong>Binary fission</strong> — Amoeba, bacteria, Paramoecium (parent divides into two).</li><li><strong>Budding</strong> — yeast, Hydra, sponges (outgrowth detaches).</li><li><strong>Fragmentation</strong> — fungi, filamentous algae, protonema of mosses.</li><li><strong>Spores</strong> — <strong>Zoospores</strong> (motile, flagellated, in Chlamydomonas); <strong>conidia</strong> (Penicillium); <strong>gemmules</strong> (sponges); <strong>bulbils</strong> (Agave).</li></ul><p>In <strong>unicellular organisms</strong> growth and reproduction are synonymous. Asexual reproduction is <strong>fast and simple</strong> but produces little variation.</p>",
            },
            {
                "id": "ro-vegetative",
                "level": 2,
                "heading": "4. Vegetative propagation",
                "html": "<p><strong>Vegetative propagation</strong> in plants — new plants from vegetative parts (asexual, used in horticulture):</p><ul><li><strong>Rhizome</strong> — banana, ginger, turmeric.</li><li><strong>Tuber</strong> — potato (eyes = buds).</li><li><strong>Bulb</strong> — onion, garlic.</li><li><strong>Offset</strong> — water hyacinth (<em>Eichhornia</em>).</li><li><strong>Runner/stolon</strong> — grass, strawberry (not water hyacinth).</li><li><strong>Adventitious buds</strong> — notches on <em>Bryophyllum</em> leaves; bulbils on <em>Agave</em>.</li></ul><p><strong>Water hyacinth</strong> ('Terror of Bengal') — fastest-spreading aquatic weed; clogs water bodies, kills fish by deoxygenation. <strong>Parthenocarpic</strong> fruits (e.g. banana) develop without fertilisation.</p>",
            },
            {
                "id": "ro-sexual-basics",
                "level": 2,
                "heading": "5. Sexual reproduction — events & meiosis",
                "html": "<p><strong>Sexual reproduction</strong> involves: (i) pre-fertilisation (gametogenesis), (ii) <strong>fertilisation/syngamy</strong> (fusion of gametes → zygote), (iii) post-fertilisation (embryogenesis). <strong>Gametes</strong> are usually <strong>haploid</strong>; formed from diploid <strong>meiocytes</strong> by <strong>meiosis</strong> (reduces chromosome number by half). <strong>Syngamy</strong> restores diploidy in the zygote. The most critical event is <strong>fertilisation</strong>. Offspring show <strong>more variation</strong> than asexual progeny because gametes from two parents combine qualitatively different genetic material.</p><p><strong>Haploid</strong> parental body: most fungi and some algae (e.g. Volvox, Chlamydomonas). <strong>Diploid</strong> dominant: gymnosperms, angiosperms, most animals. <strong>Ophioglossum</strong> (a fern) has the highest chromosome number among plants tested in NEET contexts.</p>",
            },
            {
                "id": "ro-fertilisation-modes",
                "level": 2,
                "heading": "6. Fertilisation strategies in animals",
                "html": "<p><strong>External fertilisation</strong> — gametes released in water; needs moist environment (most fishes, amphibians). <strong>Internal fertilisation</strong> — fusion inside the female body (reptiles, birds, mammals); associated with <strong>oviparity</strong> (egg-laying: reptiles, birds), <strong>viviparity</strong> (live birth: most mammals including humans), or <strong>ovoviviparity</strong> (egg retained in body: some sharks, lizards). <strong>Oviparous</strong> examples: frog, lizard, bird; <strong>viviparous</strong>: human, cow, dog, horse, whale. Humans are <strong>continuous breeders</strong> (reproductively active throughout adult life).</p>",
            },
            {
                "id": "ro-plants-reproduction",
                "level": 2,
                "heading": "7. Sexual reproduction in plants — special cases",
                "html": "<ul><li><strong>Monoecious</strong> — male and female flowers on same plant (cucurbits, coconut, castor, maize); prevents autogamy but not geitonogamy.</li><li><strong>Dioecious</strong> — male and female on separate plants (papaya, date palm, cannabis); prevents both autogamy and geitonogamy.</li><li><strong>Bamboo</strong> — gregarious flowering once in 12–120 years, then dies.</li><li><strong>Strobilanthus kunthiana</strong> (Neelakurinji) — flowers once in 12 years.</li><li>In <strong>bryophytes and pteridophytes</strong> male gametes are motile and need <strong>water</strong> for transfer.</li><li><strong>Chara</strong> — oogonium (female) upper, antheridium (male) lower on same plant.</li><li>After fertilisation in angiosperms: <strong>ovule → seed</strong>; <strong>ovary → fruit (pericarp)</strong>; <strong>integuments → seed coat</strong> (not pericarp).</li></ul>",
            },
        ],
    },
    {
        "id": "bio12-ch02",
        "class": 12,
        "chapterNo": 2,
        "title": "Sexual Reproduction in Flowering Plants",
        "topic": "Reproduction in Flowering Plant",
        "intro": "NCERT Class XII Chapter 1 (Unit VI): flower structure, microsporogenesis and megasporogenesis, pollination and its agents, pollen–pistil interaction, double fertilisation, post-fertilisation development of endosperm, embryo, seed and fruit, and apomixis/polyembryony.",
        "sections": [
            {
                "id": "srfp-overview",
                "level": 2,
                "heading": "1. Flower — seat of sexual reproduction",
                "html": "<p>All flowering plants (<strong>angiosperms</strong>) reproduce sexually. The <strong>flower</strong> bears <strong>androecium</strong> (stamens = male) and <strong>gynoecium</strong> (pistil = female). Flowers convey human sentiments (love, grief, etc.) and have ornamental/social value (<strong>floriculture</strong>). Male gametophyte develops in the <strong>pollen grain</strong>; female gametophyte in the <strong>embryo sac</strong> inside the ovule.</p>",
            },
            {
                "id": "srfp-anther-pollen",
                "level": 2,
                "heading": "2. Stamen, anther & pollen grain",
                "html": "<p>A stamen = <strong>filament</strong> + <strong>anther</strong>. Typical anther is <strong>bilobed, dithecous, tetrasporangiate</strong> (4 microsporangia). Wall layers: <strong>epidermis, endothecium, middle layers, tapetum</strong> (innermost; nourishes pollen; often binucleate). <strong>Microsporogenesis</strong>: PMC → meiosis → microspore tetrad → pollen grains.</p><p><strong>Pollen grain</strong> (male gametophyte): <strong>exine</strong> (sporopollenin, resistant; <strong>germ pores</strong>) + <strong>intine</strong> (cellulose/pectin). At shedding: <strong>2-celled</strong> (vegetative + generative) in &gt;60% species, or <strong>3-celled</strong> (vegetative + 2 male gametes). Rice pollen viable ~<strong>30 min</strong>; some Rosaceae/Leguminosae months. Stored in liquid N₂ as <strong>pollen banks</strong>. Parthenium causes pollen allergy. Pollen is rich in nutrients (supplements).</p>",
            },
            {
                "id": "srfp-pistil-embryosac",
                "level": 2,
                "heading": "3. Pistil, ovule & embryo sac",
                "html": "<p>Pistil = <strong>stigma + style + ovary</strong>. Ovary has locule/placenta bearing <strong>ovules</strong>. Ovule: <strong>funicle, hilum, integuments, micropyle, chalaza, nucellus, embryo sac</strong>. <strong>Megasporogenesis</strong>: MMC → meiosis → 4 megaspores; usually <strong>monosporic</strong> (one functional). Embryo sac development: free nuclear divisions → <strong>8-nucleate, 7-celled</strong> at maturity:</p><ul><li><strong>Egg apparatus</strong> (micropylar): 2 <strong>synergids</strong> (with <strong>filiform apparatus</strong>) + 1 <strong>egg</strong>.</li><li><strong>Antipodals</strong> (3) at chalaza.</li><li><strong>Central cell</strong> with 2 <strong>polar nuclei</strong>.</li></ul>",
            },
            {
                "id": "srfp-pollination",
                "level": 2,
                "heading": "4. Pollination — types & agents",
                "html": "<p><strong>Pollination</strong> = transfer of pollen from anther to stigma.</p><ul><li><strong>Autogamy</strong> — same flower. <strong>Cleistogamous</strong> flowers (Viola, Oxalis, Commelina) never open; assured self-pollination.</li><li><strong>Geitonogamy</strong> — another flower, same plant (genetically like autogamy).</li><li><strong>Xenogamy</strong> — different plant; only true cross-pollination.</li></ul><p><strong>Agents</strong>: wind (<strong>anemophily</strong> — coconut, maize, grass; light non-sticky pollen, feathery stigma), water (<strong>hydrophily</strong> — Vallisneria, Hydrilla, Zostera; ~30 genera), animals (<strong>entomophily</strong> — large, colourful, fragrant, nectar; cucumber needs insects). <strong>Emasculation + bagging</strong> for artificial hybridisation of bisexual flowers.</p>",
            },
            {
                "id": "srfp-outbreeding",
                "level": 2,
                "heading": "5. Outbreeding devices & self-incompatibility",
                "html": "<p>To avoid <strong>inbreeding depression</strong>, plants evolved: (i) pollen release and stigma receptivity not synchronised; (ii) anther and stigma at different positions; (iii) <strong>self-incompatibility</strong> (genetic — inhibits pollen germination/tube growth); (iv) <strong>unisexual flowers</strong> (monoecious or dioecious). <strong>Unisexuality</strong> prevents autogamy but not geitonogamy; <strong>dioecy</strong> prevents both. Emasculation not needed in unisexual female flowers.</p>",
            },
            {
                "id": "srfp-pollen-pistil",
                "level": 2,
                "heading": "6. Pollen–pistil interaction",
                "html": "<p>Stigma recognises compatible vs incompatible pollen (chemical dialogue). Compatible pollen germinates on stigma → <strong>pollen tube</strong> grows through style → enters ovule via <strong>micropyle</strong> → penetrates a synergid via <strong>filiform apparatus</strong>. If pollen shed at 2-celled stage, generative cell divides in the tube. Events from pollen deposition to tube entry = <strong>pollen–pistil interaction</strong>. Rejection illustrates self-/interspecific incompatibility.</p>",
            },
            {
                "id": "srfp-double-fert",
                "level": 2,
                "heading": "7. Double fertilisation",
                "html": "<p>Unique to <strong>angiosperms</strong>. Two fusions in embryo sac:</p><ul><li><strong>Syngamy</strong> — one male gamete + egg → <strong>diploid zygote</strong>.</li><li><strong>Triple fusion</strong> — other male gamete + 2 polar nuclei → <strong>triploid PEN</strong> (primary endosperm nucleus).</li></ul><p>PEN → primary endosperm cell → <strong>endosperm</strong>; zygote → <strong>embryo</strong>. <strong>Double fertilisation</strong> = syngamy + triple fusion.</p>",
            },
            {
                "id": "srfp-post-fert",
                "level": 2,
                "heading": "8. Post-fertilisation — endosperm, embryo, seed & fruit",
                "html": "<p><strong>Endosperm</strong> develops before embryo (nutrition). Free-nuclear endosperm → cellular; tender <strong>coconut water</strong> = free-nuclear endosperm; white kernel = cellular. Non-albuminous (pea, groundnut — endosperm used up) vs albuminous (wheat, maize, castor — persistent endosperm/perisperm).</p><p><strong>Embryo</strong>: proembryo → globular → heart-shaped → mature. Dicot: epicotyl (plumule), hypocotyl, radicle, 2 cotyledons. Monocot grass: <strong>scutellum</strong>, coleoptile, coleorhiza.</p><p><strong>Seed</strong> = fertilised ovule (testa/tegmen from integuments; micropyle pore). <strong>Fruit</strong> = mature ovary (pericarp). <strong>False fruits</strong> (apple, strawberry — thalamus contributes). <strong>Parthenocarpic</strong> fruits (banana) without fertilisation.</p>",
            },
            {
                "id": "srfp-apomixis",
                "level": 2,
                "heading": "9. Apomixis & polyembryony",
                "html": "<p><strong>Apomixis</strong> — seed formation <strong>without fertilisation</strong> (asexual mimicry; grasses, Asteraceae, Citrus, Mango). Diploid egg or nucellar cells form embryos directly. <strong>Polyembryony</strong> — &gt;1 embryo per seed (Citrus, Mango — nucellar embryos). Apomictic embryos are <strong>clones</strong>. Useful for fixing hybrid characters without yearly hybrid seed production.</p>",
            },
        ],
    },
    {
        "id": "bio12-ch03",
        "class": 12,
        "chapterNo": 3,
        "title": "Human Reproduction",
        "topic": "Human Reproduction",
        "intro": "NCERT Class XII Chapter 2: male and female reproductive systems, gametogenesis, the menstrual cycle, fertilisation and implantation, pregnancy and embryonic development, parturition and lactation.",
        "sections": [
            {
                "id": "hr-overview",
                "level": 2,
                "heading": "1. Overview of human reproduction",
                "html": "<p>Humans are <strong>sexually reproducing, viviparous</strong> mammals. Events: <strong>gametogenesis</strong> → <strong>insemination</strong> → <strong>fertilisation</strong> (ampulla of oviduct) → <strong>cleavage</strong> → <strong>blastocyst</strong> → <strong>implantation</strong> → <strong>gestation</strong> (~9 months) → <strong>parturition</strong> → <strong>lactation</strong>. Spermatogenesis continues in old age; oogenesis ceases at ~50 years (<strong>menopause</strong>).</p>",
            },
            {
                "id": "hr-male",
                "level": 2,
                "heading": "2. Male reproductive system",
                "html": "<p><strong>Testes</strong> in <strong>scrotum</strong> (2–2.5°C below body temp). Each testis ~250 <strong>testicular lobules</strong> with <strong>seminiferous tubules</strong> (spermatogonia + <strong>Sertoli cells</strong>) and interstitial <strong>Leydig cells</strong> (androgens). Ducts: rete testis → vasa efferentia → <strong>epididymis</strong> → <strong>vas deferens</strong> → ejaculatory duct → urethra. Accessory glands: <strong>seminal vesicles, prostate, bulbourethral (Cowper's)</strong> — <strong>seminal plasma</strong> rich in <strong>fructose, calcium, enzymes</strong>. <strong>Penis</strong> with glans and foreskin. LH stimulates Leydig cells; FSH acts on Sertoli cells.</p>",
            },
            {
                "id": "hr-female",
                "level": 2,
                "heading": "3. Female reproductive system",
                "html": "<p><strong>Ovaries</strong> (2–4 cm; cortex + medulla) produce ova and ovarian hormones. <strong>Oviducts</strong> (10–12 cm): infundibulum with <strong>fimbriae</strong> → ampulla (fertilisation site) → isthmus. <strong>Uterus</strong>: perimetrium, myometrium, <strong>endometrium</strong> (cyclical). Opens to vagina via <strong>cervix/cervical canal</strong> (birth canal with vagina). External genitalia: mons pubis, labia majora/minora, hymen (unreliable virginity indicator), <strong>clitoris</strong> (junction of labia minora). <strong>Mammary glands</strong>: 15–20 lobes, alveoli, lactiferous ducts.</p>",
            },
            {
                "id": "hr-spermatogenesis",
                "level": 2,
                "heading": "4. Spermatogenesis & sperm structure",
                "html": "<p><strong>Spermatogonia</strong> (diploid, 46 ch.) → mitosis → primary spermatocytes → meiosis I → secondary spermatocytes (23) → meiosis II → <strong>spermatids</strong> (23) → <strong>spermiogenesis</strong> → spermatozoa; released by <strong>spermiation</strong>. Triggered at puberty by ↑<strong>GnRH</strong> → LH + FSH.</p><p><strong>Sperm</strong>: head (<strong>acrosome</strong> with enzymes + haploid nucleus), neck, middle piece (mitochondria for motility), tail. ~200–300 million/ejaculate; fertility needs ≥60% normal morphology, ≥40% motility. Viable up to ~<strong>48–72 h</strong> in female tract.</p>",
            },
            {
                "id": "hr-oogenesis",
                "level": 2,
                "heading": "5. Oogenesis & folliculogenesis",
                "html": "<p><strong>Oogonia</strong> form in fetal ovary; arrest at prophase I as <strong>primary oocytes</strong>. At birth ~2 million; at puberty ~60,000–80,000 <strong>primary follicles</strong>. Maturation: primary follicle → secondary → tertiary (antrum; <strong>theca interna/externa</strong>) → <strong>Graafian follicle</strong>. Primary oocyte completes meiosis I → <strong>secondary oocyte</strong> + 1st polar body; meiosis II completes after sperm entry. <strong>Ovulation</strong> releases secondary oocyte with <strong>zona pellucida</strong> and <strong>corona radiata</strong>.</p>",
            },
            {
                "id": "hr-menstrual",
                "level": 2,
                "heading": "6. Menstrual cycle",
                "html": "<p>In female primates; begins at <strong>menarche</strong>; ~<strong>28/29 days</strong>. Phases: (1) <strong>Menstrual</strong> (3–5 days) — endometrial breakdown if no fertilisation. (2) <strong>Follicular/proliferative</strong> — follicles grow, estrogen from follicles rebuilds endometrium. (3) <strong>Ovulatory</strong> (~day <strong>14</strong>) — <strong>LH surge</strong> ruptures Graafian follicle. (4) <strong>Luteal/secretory</strong> — <strong>corpus luteum</strong> secretes <strong>progesterone</strong> (maintains endometrium for implantation). Without fertilisation, corpus luteum degenerates → menstruation. Cycle ceases in <strong>pregnancy</strong> and at <strong>menopause</strong> (~50 years).</p>",
            },
            {
                "id": "hr-fertilization",
                "level": 2,
                "heading": "7. Fertilisation, cleavage & implantation",
                "html": "<p>Fertilisation in <strong>ampulla</strong> of oviduct (requires simultaneous transport of sperm and ovum). Sperm binds <strong>zona pellucida</strong>; acrosome enzymes aid entry; <strong>polyspermy block</strong>. Secondary oocyte completes meiosis II → ovum; pronuclei fuse → <strong>diploid zygote (46)</strong>. <strong>Sex determined by sperm</strong> (X or Y); ovum always X.</p><p>Cleavage in isthmus: 2 → 4 → 8 … <strong>blastomeres</strong>; 8–16 cell = <strong>morula</strong> → <strong>blastocyst</strong> (<strong>trophoblast</strong> + inner cell mass). <strong>Implantation</strong> in endometrium → pregnancy.</p>",
            },
            {
                "id": "hr-pregnancy",
                "level": 2,
                "heading": "8. Pregnancy & embryonic development",
                "html": "<p><strong>Placenta</strong> — chorionic villi + uterine tissue; connected by <strong>umbilical cord</strong>; exchange of O₂/nutrients/wastes; endocrine organ (hCG, hPL, estrogens, progestogens). <strong>Relaxin</strong> from ovary in late pregnancy.</p><p>Germ layers from inner cell mass: <strong>ectoderm, mesoderm, endoderm</strong>. Timeline: heart ~1 month; limbs by 2 months; organ systems by <strong>12 weeks</strong> (1st trimester); first foetal movements ~5th month; eyelids separate ~24 weeks. Gestation ~<strong>9 months</strong>.</p>",
            },
            {
                "id": "hr-parturition",
                "level": 2,
                "heading": "9. Parturition & lactation",
                "html": "<p><strong>Parturition</strong> — expulsion of foetus via birth canal (cervix + vagina). Induced by foetal-placental signals → <strong>foetal ejection reflex</strong> → <strong>oxytocin</strong> (positive feedback on uterine contractions). <strong>Placenta</strong> expelled after baby. <strong>Lactation</strong> — mammary glands produce milk; initial secretion = <strong>colostrum</strong> (antibodies for newborn immunity). Breast-feeding recommended early months.</p>",
            },
        ],
    },
    {
        "id": "bio12-ch04",
        "class": 12,
        "chapterNo": 4,
        "title": "Reproductive Health",
        "topic": "Reproductive Health",
        "intro": "NCERT Class XII Chapter 3: WHO definition of reproductive health, India's RCH programmes, population stabilisation, contraceptive methods, MTP, sexually transmitted infections, and infertility with assisted reproductive technologies.",
        "sections": [
            {
                "id": "rh-overview",
                "level": 2,
                "heading": "1. Reproductive health & RCH programmes",
                "html": "<p><strong>Reproductive health</strong> (WHO) = total well-being in all aspects of reproduction — physical, emotional, behavioural, social. India initiated <strong>family planning (1951)</strong> and now <strong>Reproductive and Child Health Care (RCH)</strong> programmes: awareness (adolescence, safe sex, STDs/AIDS), medical care (pregnancy, delivery, contraception, infertility), statutory ban on <strong>amniocentesis for sex determination</strong>. <strong>CDRI</strong> (Lucknow) developed <strong>Saheli</strong> (non-steroidal oral contraceptive). <strong>WHO</strong> = World Health Organization.</p>",
            },
            {
                "id": "rh-population",
                "level": 2,
                "heading": "2. Population explosion & birth control goals",
                "html": "<p>World population: ~2 billion (1900) → ~6 billion (2000) → <strong>7.2 billion (2011)</strong>. India: ~350 million (1947) → ~1 billion (2000) → <strong>1.2+ billion (2011)</strong>; growth rate &lt;2%. Causes: ↓death rate/MMR/IMR, more people in reproductive age. Strategies: <strong>Hum Do Hamare Do</strong>, raising marriageable age (female <strong>18</strong>, male <strong>21</strong>), incentives for small families, contraception.</p>",
            },
            {
                "id": "rh-natural-barrier",
                "level": 2,
                "heading": "3. Natural & barrier contraception",
                "html": "<p><strong>Natural/traditional</strong>: <strong>periodic abstinence</strong> (avoid coitus days <strong>10–17</strong>, fertile period); <strong>coitus interruptus</strong> (withdrawal); <strong>lactational amenorrhea</strong> (effective up to <strong>6 months</strong> of intense lactation — suppresses gonadotropins). No side effects but higher failure rates.</p><p><strong>Barrier</strong>: <strong>condoms</strong> (Nirodh — male; female condom covers vagina/cervix); diaphragms, cervical caps, vaults + spermicidal jellies. Prevent semen entry; also protect against <strong>STIs/AIDS</strong>.</p>",
            },
            {
                "id": "rh-iud-oral",
                "level": 2,
                "heading": "4. IUDs, oral pills & injectables",
                "html": "<p><strong>IUDs</strong> (Lippes loop; copper — <strong>CuT, Cu7, Multiload 375</strong>; hormone — <strong>Progestasert, LNG-20</strong>): inserted in uterus; ↑phagocytosis of sperm; Cu²⁺ suppresses sperm motility; hormone IUDs make uterus unsuitable for implantation and cervix hostile to sperm. Ideal for spacing/delaying pregnancy.</p><p><strong>Oral pills</strong>: progestogen or progestogen–estrogen, 21 days + 7-day gap; inhibit ovulation, alter cervical mucus. <strong>Saheli</strong> — once-a-week, non-steroidal. <strong>Injectables/implants</strong> (Figure 3.3). <strong>Emergency contraception</strong> within <strong>72 h</strong> of coitus.</p>",
            },
            {
                "id": "rh-surgical",
                "level": 2,
                "heading": "5. Surgical sterilisation",
                "html": "<p><strong>Sterilisation</strong> — terminal method blocking gamete transport. <strong>Vasectomy</strong> (male): small part of <strong>vas deferens</strong> tied/removed via scrotal incision. <strong>Tubectomy</strong> (female): part of <strong>fallopian tube</strong> tied/removed. Highly effective; <strong>poor reversibility</strong>. Does <strong>not</strong> stop gamete formation.</p>",
            },
            {
                "id": "rh-mtp",
                "level": 2,
                "heading": "6. Medical Termination of Pregnancy (MTP)",
                "html": "<p><strong>MTP</strong> — intentional termination before full term; legalised in India <strong>1971</strong>. ~<strong>45–50 million</strong>/year worldwide. Safest in <strong>first trimester (≤12 weeks)</strong>; one registered practitioner's opinion sufficient within 12 weeks; <strong>two practitioners</strong> for 12–24 weeks (Amendment Act 2017). Misuse of <strong>amniocentesis + MTP for female foeticide</strong> is illegal. Second trimester abortions riskier.</p>",
            },
            {
                "id": "rh-std",
                "level": 2,
                "heading": "7. Sexually transmitted infections (STIs)",
                "html": "<p><strong>STIs/RTIs/VD</strong>: Gonorrhoea (<em>Neisseria</em>), Syphilis (<em>Treponema</em>), Genital herpes, Chlamydia, Genital warts (HPV), Trichomoniasis, Hepatitis-B, <strong>HIV/AIDS</strong>. High incidence in age group <strong>15–24</strong>. Prevention: avoid unknown/multiple partners; <strong>condoms</strong>; early treatment. Hepatitis-B, herpes, HIV not fully curable. Complications: PID, infertility, still birth, ectopic pregnancy. Females often asymptomatic early.</p>",
            },
            {
                "id": "rh-infertility",
                "level": 2,
                "heading": "8. Infertility & assisted reproductive technology (ART)",
                "html": "<p><strong>Infertility</strong> — unable to conceive after <strong>2 years</strong> of unprotected cohabitation; male and female causes both common. <strong>ART</strong>:</p><ul><li><strong>IVF + ET</strong> ('test tube baby') — zygote/early embryo (≤8 blastomeres) transferred to uterus (<strong>IUT</strong>) or <strong>ZIFT</strong> (zygote to fallopian tube).</li><li><strong>GIFT</strong> — ovum + sperm transferred to fallopian tube (requires functional tubes).</li><li><strong>ICSI</strong> — sperm injected into ovum.</li><li><strong>AI/IUI</strong> — artificial insemination (semen into vagina or uterus).</li></ul><p>Legal <strong>adoption</strong> is also encouraged. Infertility clinics diagnose and treat reproductive disorders.</p>",
            },
        ],
    },
]

RULESETS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "bio12-ch01": (
        "ro-overview",
        [
            ("ro-vegetative", r"water hyacinth|eichhornia|terror of bengal|rhizome|tuber|offset|runner|stolon|bulbil|adventitious bud|bryophyllum|banana|ginger|turmeric|potato|onion|garlic|strawberry|vegetative propag|offset|agave"),
            ("ro-asexual", r"binary fission|budding|fragmentation|zoospore|conidia|gemmule|chlamydomonas|penicillium|hydra|yeast|spore|clone|amoeba.{0,20}fission|unicellular"),
            ("ro-plants-reproduction", r"monoecious|dioecious|bamboo|strobilanthus|neelakurinji|chara|oogonium|antheridium|bryophyte|pteridophyte|male gamete.{0,20}water|ovule.{0,15}seed|ovary.{0,15}fruit|pericarp|seed coat|integument|papaya|coconut|cucurbit|castor|maize|gregarious"),
            ("ro-fertilisation-modes", r"ovipar|vivipar|ovovivipar|external fertil|internal fertil|continuous breeder|horse|whale|lizard|bird|mammal|fish|amphibian"),
            ("ro-sexual-basics", r"meiosis|meiocyte|gamete|syngamy|zygote|fertiliz|haploid|diploid|ophioglossum|variation.{0,20}sexual|volvox|fungi.{0,15}haploid|parthenocarp"),
            ("ro-lifespan", r"life span|lifespan|tortoise|peepal|banyan|butterfly|crow|elephant|longest living"),
        ],
    ),
    "bio12-ch02": (
        "srfp-overview",
        [
            ("srfp-apomixis", r"apomixis|polyembryony|nucellar embryo|citrus|mango.{0,15}embryo|clone.{0,15}apomict"),
            ("srfp-post-fert", r"endosperm|embryo|scutellum|coleoptile|coleorhiza|epicotyl|hypocotyl|radicle|plumule|proembryo|globular|heart.?shaped|albuminous|non.?albuminous|ex.?albuminous|perisperm|pericarp|false fruit|parthenocarp|seed coat|micropyle|cotyledon|monocot.{0,15}embryo|dicot.{0,15}embryo|coconut water|cellular endosperm|free.?nuclear endosperm"),
            ("srfp-double-fert", r"double fertil|triple fusion|polar nucle|pen\b|primary endosperm|syngamy|male gamete.{0,20}egg|male gamete.{0,20}central"),
            ("srfp-pollen-pistil", r"pollen.?pistil|pollen tube|filiform apparatus|synergid|germ pore|incompatibility|reject|compatible pollen|emasculation|bagging|artificial hybrid"),
            ("srfp-outbreeding", r"self.?incompat|inbreeding|outbreeding|geitonogamy|autogamy|xenogamy|cleistogam|chasmogam|unisexual|emasculat|prevent self"),
            ("srfp-pollination", r"pollinat|anemophil|entomophil|hydrophil|zoophil|wind.?pollin|water.?pollin|insect.?pollin|vallisneria|hydrilla|zostera|maize|coconut|feather.{0,10}stigma|nectar|fragran|yucca|amorphophallus"),
            ("srfp-pistil-embryosac", r"embryo sac|megaspor|mmc|ovule|pistil|stigma|style|ovary|integument|micropyle|chalaza|nucellus|funicle|hilum|monosporic|egg apparatus|antipodal|polar nucle|7.?cell|8.?nucleat|synergid|egg cell|female gametophyte"),
            ("srfp-anther-pollen", r"pollen|anther|stamen|microspor|tapetum|endothecium|sporopollenin|exine|intine|generative cell|vegetative cell|pmc|pollen mother|tetrad|2.?celled|3.?celled|parthenium|pollen bank|viability|germ pore|androecium|filament"),
        ],
    ),
    "bio12-ch03": (
        "hr-overview",
        [
            ("hr-parturition", r"parturition|lactation|colostrum|oxytocin|foetal ejection|birth canal|mammary|breast.?feed|delivery|expulsion|placenta.{0,15}expel|after.{0,10}delivery"),
            ("hr-pregnancy", r"pregnancy|gestation|placenta|chorionic villi|umbilical|hcg|hpl|relaxin|trophoblast|inner cell mass|ectoderm|mesoderm|endoderm|trimester|foetus|fetus|implant"),
            ("hr-fertilization", r"fertiliz|zygote|blastocyst|morula|blastomere|cleavage|zona pellucida|corona radiata|acrosome|ampulla|inseminat|sex of.{0,10}baby|sex chromosom|polyspermy|implantation"),
            ("hr-menstrual", r"menstrual|menstruation|menarche|menopause|follicular phase|luteal phase|ovulation|lh surge|corpus luteum|progesterone|endometri|graafian|day 14|28 day|29 day|proliferative|secretory phase"),
            ("hr-oogenesis", r"oogenesis|oogonium|primary oocyte|secondary oocyte|ovulation|follicle|graafian|antrum|theca|polar body|corpus albicans|oocyte"),
            ("hr-spermatogenesis", r"spermatogonia|spermatogenesis|spermiogenesis|spermiation|spermatid|spermatocyte|seminiferous|sertoli|leydig|androgen|sperm tail|middle piece|mitochondria.{0,15}sperm|acrosome|gnrh|60 per cent|40 per cent|200.{0,10}million"),
            ("hr-female", r"ovary|oviduct|fallopian|uterus|cervix|vagina|fimbriae|infundibulum|isthmus|labia|clitoris|hymen|mons pubis|mammary|endometrium|myometrium|perimetrium|birth canal"),
            ("hr-male", r"testis|testes|scrotum|epididymis|vas deferens|seminal vesicle|prostate|bulbourethral|cowper|penis|ejaculatory|seminiferous|rete testis|vasa efferentia|seminal plasma|fructose|leydig|sertoli|androgen"),
        ],
    ),
    "bio12-ch04": (
        "rh-overview",
        [
            ("rh-infertility", r"infertilit|ivf|gift|zift|icsi|iui|artificial insemin|test tube baby|embryo transfer|blastomere|surrogacy|adoption|infertility clinic"),
            ("rh-std", r"std|sti|rti|venereal|gonorrh|syphilis|herpes|chlamyd|trichomon|hepatitis.?b|hiv|aids|hpv|genital wart|15.{0,5}24|sexually transmitted"),
            ("rh-mtp", r"mtp|medical termination|abort|amniocentesis|female foeticide|foeticide|trimester|12 week|24 week|registered medical practitioner"),
            ("rh-surgical", r"vasectomy|tubectomy|sterilis|vas deferens.{0,15}remov|fallopian.{0,15}remov|surgical method"),
            ("rh-iud-oral", r"\biud\b|lippes loop|cut\b|cu7|multiload|lng.?20|progestasert|oral pill|contraceptive pill|saheli|implant|injectable|emergency contrace|72 hour|progesterone.{0,15}pill|oestrogen.{0,15}combin"),
            ("rh-natural-barrier", r"condom|nirodh|barrier|diaphragm|cervical cap|vault|spermicid|periodic abstinence|coitus interruptus|withdrawal|lactational amenorr|abstain.{0,10}day 10|fertile period"),
            ("rh-population", r"population|7\.2 billion|1\.2 billion|hum do|marriageable age|birth control|family planning|growth rate|fertile couple"),
        ],
    ),
}

EXPECTED = {
    "bio12-ch01": 139,
    "bio12-ch02": 602,
    "bio12-ch03": 570,
    "bio12-ch04": 358,
}


def merge() -> None:
    notes = json.loads((ROOT / "notes.json").read_text(encoding="utf-8"))
    note_links = json.loads((ROOT / "note_links.json").read_text(encoding="utf-8"))

    for chapter in CHAPTERS:
        cid = chapter["id"]
        topic = chapter["topic"]
        default, ruleset = RULESETS[cid]
        questions = load_bank(topic)
        exp = EXPECTED[cid]
        if len(questions) != exp:
            print(f"WARN {cid}: bank count {len(questions)} != expected {exp}")

        links = build_links(questions, ruleset, default)
        upsert_chapter_notes(notes, chapter)
        upsert_chapter_links(note_links, cid, topic, links)

        dist = Counter(links.values())
        print(f"\n{cid} ({topic}): {len(chapter['sections'])} sections, {len(links)} links")
        for sec, cnt in dist.most_common():
            print(f"  {cnt:4d} {sec}")
        print(f"  default ({default}): {dist[default]}")

    (ROOT / "notes.json").write_text(
        json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "note_links.json").write_text(
        json.dumps(note_links, ensure_ascii=False, indent=0) + "\n", encoding="utf-8"
    )
    print("\nWrote notes.json and note_links.json")


if __name__ == "__main__":
    merge()
    errs = verify_all()
    if errs:
        for e in errs:
            print(e)
        sys.exit(1)
    print("Python verify: all chapters pass.")
