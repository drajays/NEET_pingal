#!/usr/bin/env python3
"""Merge notes + MCQ links for Transport, Mineral Nutrition, Plant Growth, Digestion."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from note_pipeline import (  # noqa: E402
    build_links,
    load_bank,
    norm_key,
    upsert_chapter_links,
    upsert_chapter_notes,
    verify_all,
)

# ── Chapter notes ──────────────────────────────────────────────────────────────

CHAPTERS: list[dict] = [
    {
        "id": "bio11-ch-transport",
        "class": 11,
        "chapterNo": 11,
        "title": "Transport in Plants",
        "topic": "Transport in Plants",
        "intro": "NCERT Class XI Chapter 11: how water and minerals move through plant cells, tissues and the whole plant — diffusion, osmosis, water potential, pathways in roots, root pressure, the cohesion–tension theory of xylem sap ascent, transpiration and phloem translocation.",
        "sections": [
            {
                "id": "tp-overview",
                "level": 2,
                "heading": "1. Transport at different levels",
                "html": "<p>Plants are less mobile than animals and need a <strong>specialised system for uptake, transport and storage of water, nutrients and photosynthates</strong>. Transport occurs at three levels: (i) <strong>cell to cell</strong> — short distances across membranes and through plasmodesmata; (ii) <strong>tissue level</strong> — movement through vascular tissues; (iii) <strong>whole plant</strong> — long-distance transport in xylem and phloem. Water and minerals absorbed by roots move upward through the <strong>xylem</strong>; organic solutes (mainly sucrose) are translocated through the <strong>phloem</strong> from source to sink.</p>",
            },
            {
                "id": "tp-diffusion-osmosis",
                "level": 2,
                "heading": "2. Diffusion, facilitated diffusion & osmosis",
                "html": "<p><strong>Diffusion</strong> is the passive movement of substances along a concentration gradient — gases and small lipophilic molecules cross membranes directly. <strong>Facilitated diffusion</strong> uses membrane <strong>channel and carrier proteins</strong> (no ATP); it is faster than simple diffusion and shows saturation kinetics. <strong>Osmosis</strong> is the diffusion of water across a <strong>semi-permeable membrane</strong>. In a hypotonic solution cells swell (may burst in animal cells); in hypertonic solution they shrink (<strong>exosmosis</strong> — excessive fertiliser can cause water stress this way); in isotonic solution there is no net water movement.</p>",
            },
            {
                "id": "tp-water-potential",
                "level": 2,
                "heading": "3. Water potential (Ψ)",
                "html": "<p><strong>Water potential (Ψ)</strong> is the potential energy of water per unit volume relative to pure water. <strong>Pure water at standard temperature has Ψ = 0</strong> (the reference). Solute lowers Ψ (<strong>solute potential Ψ<sub>s</sub></strong>, always negative); pressure raises Ψ (<strong>pressure potential Ψ<sub>p</sub></strong>). Ψ = Ψ<sub>p</sub> + Ψ<sub>s</sub>. Water moves from a region of <strong>higher (less negative) Ψ</strong> to <strong>lower (more negative) Ψ</strong>. In a flaccid plant cell Ψ<sub>p</sub> ≈ 0; in a turgid cell Ψ<sub>p</sub> is positive.</p>",
            },
            {
                "id": "tp-imbibition",
                "level": 2,
                "heading": "4. Imbibition",
                "html": "<p><strong>Imbibition</strong> is the swelling of solid colloids when they absorb water — a type of diffusion where water is adsorbed with a <strong>large increase in volume</strong> and development of imbibition pressure. Classic examples: <strong>dry seeds and wood</strong> absorbing water (prehistoric man used swelling wood to split rocks). Imbibition requires hydrophilic colloids and a water potential gradient.</p>",
            },
            {
                "id": "tp-active-transport",
                "level": 2,
                "heading": "5. Active transport & mineral uptake",
                "html": "<p><strong>Active transport</strong> moves ions/molecules <strong>against a concentration gradient</strong> using ATP and carrier proteins. Plant roots absorb mineral ions from soil; uptake is selective and can be inhibited by <strong>anaerobic conditions</strong> (lack of ATP). Membrane proteins for facilitated diffusion and active transport show <strong>enzyme-like properties</strong>: saturation, specificity and sensitivity to inhibitors.</p>",
            },
            {
                "id": "tp-pathways",
                "level": 2,
                "heading": "6. Apoplastic & symplastic pathways",
                "html": "<p>Water in roots can move by two pathways: <strong>Apoplastic</strong> — through cell walls and intercellular spaces (does not cross living membranes until the <strong>Casparian strip</strong> of the endodermis blocks further apoplastic movement); <strong>Symplastic</strong> — through cytoplasm via plasmodesmata, cell to cell. Most water in roots ultimately enters the xylem via the symplast after crossing endodermal cells.</p>",
            },
            {
                "id": "tp-root-pressure",
                "level": 2,
                "heading": "7. Root pressure & guttation",
                "html": "<p><strong>Root pressure</strong> is the positive pressure developed in xylem when ions are actively pumped into the stele and water follows osmotically — it can push water a few metres and is seen when transpiration is low. <strong>Guttation</strong> (water droplets at leaf margins through hydathodes) is caused by <strong>root pressure</strong>, not transpiration. Root pressure alone cannot account for water rise in tall trees.</p>",
            },
            {
                "id": "tp-xylem",
                "level": 2,
                "heading": "8. Xylem transport & cohesion–tension",
                "html": "<p>Water rises in xylem mainly by the <strong>transpiration pull</strong> (cohesion–tension theory): evaporation from leaves creates tension; the continuous water column is pulled upward. The <strong>cohesive</strong> and <strong>adhesive</strong> properties of water maintain the column. <strong>Transpiration pull and root pressure</strong> act as pulling and pushing forces respectively. In rooted plants xylem transport of water and minerals is essentially <strong>unidirectional (upward)</strong>.</p>",
            },
            {
                "id": "tp-transpiration",
                "level": 2,
                "heading": "9. Transpiration",
                "html": "<p><strong>Transpiration</strong> is loss of water vapour from aerial parts, mainly through <strong>stomata</strong> (also cuticle and lenticels). Guard cells regulate stomatal aperture. Factors affecting rate: light, temperature, humidity, wind and available soil water. Adaptations to reduce water loss include sunken stomata, thick cuticle and C₄/Kranz anatomy. At higher altitude (lower atmospheric pressure) transpiration rate increases. Plants obtain most carbon from the <strong>atmosphere (CO₂)</strong>, not soil.</p>",
            },
            {
                "id": "tp-phloem",
                "level": 2,
                "heading": "10. Phloem translocation",
                "html": "<p>Organic solutes (mainly <strong>sucrose</strong>) are translocated through <strong>sieve tube members</strong> from <strong>source</strong> (photosynthetic leaves, storage organs) to <strong>sink</strong> (roots, fruits, growing tips). Source and sink can <strong>reverse</strong> seasonally (e.g. tap root as source in early spring). The <strong>pressure-flow (mass-flow) hypothesis</strong> explains translocation: loading at source raises Ψ, unloading at sink lowers it, generating bulk flow. <strong>P-proteins</strong> and companion cells support sieve-tube function.</p>",
            },
        ],
    },
    {
        "id": "bio11-ch-mineral",
        "class": 11,
        "chapterNo": 12,
        "title": "Mineral Nutrition",
        "topic": "Mineral Nutrition",
        "intro": "NCERT Class XI Chapter 12: essential mineral elements, criteria of essentiality, macro- and micronutrients, deficiency symptoms, the nitrogen cycle, biological nitrogen fixation and hydroponics.",
        "sections": [
            {
                "id": "mn-overview",
                "level": 2,
                "heading": "1. Essential mineral elements",
                "html": "<p>Plants obtain minerals from soil solution. Of ~105 known elements, <strong>17 are essential</strong> for plant growth. They are classified by <strong>quantitative requirement</strong>: <strong>macronutrients</strong> (C, H, O, N, P, K, Ca, Mg, S — needed in large amounts) and <strong>micronutrients</strong> (Fe, Mn, Cu, Mo, B, Zn, Cl, Ni — needed in traces). Structural elements of the cell are <strong>C, H, O, N</strong>; <strong>P</strong> is required for all phosphorylation reactions.</p>",
            },
            {
                "id": "mn-criteria",
                "level": 2,
                "heading": "2. Criteria of essentiality & critical concentration",
                "html": "<p>Arnon and Stout criteria: (i) essential for completing life cycle; (ii) requirement is specific, not replaceable; (iii) directly involved in metabolism. <strong>Critical concentration</strong> is the concentration of an essential element below which plant growth is retarded — deficiency symptoms appear first in <strong>younger or older tissues</strong> depending on whether the element is <strong>mobile or immobile</strong> (e.g. <strong>Ca, S, Fe are not remobilised</strong>; N, P, K are).</p>",
            },
            {
                "id": "mn-hydroponics",
                "level": 2,
                "heading": "3. Hydroponics",
                "html": "<p><strong>Hydroponics</strong> (solution culture) — growing plants in nutrient solution without soil — was demonstrated by <strong>Julius von Sachs (1860)</strong>. A balanced nutrient solution contains all essential elements in proper proportion. Used to identify essential elements and study deficiency; commercially used for vegetables and flowers.</p>",
            },
            {
                "id": "mn-absorption",
                "level": 2,
                "heading": "4. Mineral absorption & soil",
                "html": "<p>Soil supplies minerals, anchors roots and holds water. Mineral ions are absorbed mainly by root epidermal cells — <strong>active transport</strong> (needs ATP); absorption is <strong>inhibited in anaerobic conditions</strong>. <strong>Calcium</strong> affects permeability of the plasma membrane. Toxic concentration of minerals causes damage; excess of one element can induce deficiency of another.</p>",
            },
            {
                "id": "mn-macronutrients",
                "level": 2,
                "heading": "5. Macronutrients — functions & deficiency",
                "html": "<ul><li><strong>Nitrogen</strong> — component of proteins, nucleic acids, chlorophyll; deficiency → chlorosis, stunted growth.</li><li><strong>Phosphorus</strong> — nucleic acids, ATP, membrane lipids; deficiency → purple/reddish leaves, poor root growth.</li><li><strong>Potassium</strong> — enzyme activation, stomatal opening, ion balance; deficiency → yellowing of leaf margins.</li><li><strong>Calcium</strong> — cell wall (middle lamella), membrane stability; not remobilised.</li><li><strong>Magnesium</strong> — central atom of chlorophyll; activates many enzymes.</li><li><strong>Sulphur</strong> — constituent of amino acids (cysteine, methionine); deficiency causes chlorosis.</li></ul>",
            },
            {
                "id": "mn-micronutrients",
                "level": 2,
                "heading": "6. Micronutrients — functions & deficiency",
                "html": "<ul><li><strong>Iron (Fe)</strong> — chlorophyll synthesis (not a constituent); deficiency → interveinal chlorosis.</li><li><strong>Manganese (Mn)</strong> — photolysis of water in PS II; deficiency → grey spots of oats.</li><li><strong>Zinc (Zn)</strong> — auxin synthesis; deficiency → rosette habit, little leaves.</li><li><strong>Copper (Cu)</strong> — component of plastocyanin and cytochrome oxidase.</li><li><strong>Boron (B)</strong> — pollen germination, cell wall synthesis.</li><li><strong>Molybdenum (Mo)</strong> — essential for nitrogen fixation and nitrate reduction.</li><li><strong>Chlorine (Cl)</strong> — water splitting in photosynthesis.</li></ul>",
            },
            {
                "id": "mn-nitrogen-cycle",
                "level": 2,
                "heading": "7. Nitrogen cycle",
                "html": "<p>Atmospheric N₂ is fixed, assimilated by plants, passed through food chains, returned by decomposition and <strong>denitrification</strong>. Steps: <strong>nitrogen fixation</strong> → <strong>ammonification</strong> → <strong>nitrification</strong> (NH₃ → NO₂⁻ → NO₃⁻) → uptake → <strong>denitrification</strong> (NO₃⁻ back to N₂). Industrial and biological fixation replenish usable nitrogen.</p>",
            },
            {
                "id": "mn-biological-fixation",
                "level": 2,
                "heading": "8. Biological nitrogen fixation",
                "html": "<p><strong>Rhizobium</strong> (and related genera) forms <strong>root nodules</strong> on legumes (groundnut, soybean). <strong>Leg-haemoglobin</strong> (pink pigment) protects <strong>nitrogenase</strong> from O₂. <strong>Nitrogenase</strong> (Mo, Fe, protein cofactor — not Mg) reduces N₂ to <strong>ammonia</strong> (first stable product in legumes). Free-living fixers include <em>Azotobacter</em>, <em>Anabaena</em>. Nitrogenase may need low O₂ (anaerobic conditions in nodules).</p>",
            },
            {
                "id": "mn-special-modes",
                "level": 2,
                "heading": "9. Special nutritional modes",
                "html": "<p><strong>Insectivorous plants</strong> (e.g. pitcher plant, Venus flytrap) grow in nitrogen-deficient soil and trap insects for nutrition — an example of <strong>nutritional adaptation</strong>. <strong>Mycorrhiza</strong> — symbiotic association of fungi with roots — helps absorb phosphorus and other minerals. Delay in flowering can occur due to deficiency of N, P or K.</p>",
            },
        ],
    },
    {
        "id": "bio11-ch13",
        "class": 11,
        "chapterNo": 13,
        "title": "Plant Growth and Development",
        "topic": "Plant Growth and Development",
        "intro": "NCERT Class XI Chapter 13: growth (meristems, phases, growth rates), differentiation, dedifferentiation, development and plasticity, the five plant growth regulators (auxins, gibberellins, cytokinins, ethylene, ABA), and photoperiodism/vernalisation.",
        "sections": [
            {
                "id": "pgd-overview",
                "level": 2,
                "heading": "1. Growth — definition & measurement",
                "html": "<p><strong>Growth</strong> is an irreversible permanent increase in size/mass/number of cells, accompanied by anabolic and catabolic metabolism. At the cellular level growth is principally an <strong>increase in protoplasm</strong>. It is measured by fresh/dry weight, length, area, volume or cell number. Growth requires <strong>water</strong> (turgor for cell enlargement), <strong>oxygen</strong>, nutrients and optimum temperature.</p>",
            },
            {
                "id": "pgd-meristems",
                "level": 2,
                "heading": "2. Meristems & indeterminate growth",
                "html": "<p>Plant growth is generally <strong>indeterminate</strong> — meristems retain dividing capacity throughout life (<strong>open form of growth</strong>). <strong>Root and shoot apical meristems</strong> give primary growth (elongation); <strong>lateral meristems</strong> (vascular cambium, cork cambium) give secondary growth (girth). A maize root apex can produce &gt;17,500 cells/hour.</p>",
            },
            {
                "id": "pgd-phases",
                "level": 2,
                "heading": "3. Phases of growth",
                "html": "<p>Three phases along a root/shoot axis: <strong>meristematic</strong> (dividing, thin walls, dense protoplasm) → <strong>elongation</strong> (vacuolation, cell enlargement) → <strong>maturation</strong> (wall thickening, differentiation). Slow initial growth = <strong>lag phase</strong>; rapid exponential increase = <strong>log phase</strong>; slowing = <strong>senescent phase</strong>.</p>",
            },
            {
                "id": "pgd-growth-rates",
                "level": 2,
                "heading": "4. Growth rates & curves",
                "html": "<p><strong>Arithmetic growth</strong>: one daughter cell continues dividing (e.g. root elongating at constant rate; L<sub>t</sub> = L₀ + rt). <strong>Geometric growth</strong>: both progeny divide (exponential; W₁ = W₀e<sup>rt</sup>). Plotted against time → <strong>sigmoid (S) curve</strong> (lag → log → stationary). <strong>Absolute growth rate</strong> = total growth per unit time; <strong>relative growth rate</strong> = growth per unit initial size.</p>",
            },
            {
                "id": "pgd-differentiation",
                "level": 2,
                "heading": "5. Differentiation, dedifferentiation & redifferentiation",
                "html": "<p><strong>Differentiation</strong> — cells mature structurally/functionally (e.g. tracheary elements lose protoplasm, develop lignified secondary walls). <strong>Dedifferentiation</strong> — differentiated cells regain division capacity (e.g. interfascicular cambium from parenchyma). <strong>Redifferentiation</strong> — dedifferentiated cells mature again. Differentiation in plants is <strong>open</strong> — same meristem gives different tissues depending on position.</p>",
            },
            {
                "id": "pgd-development",
                "level": 2,
                "heading": "6. Development & plasticity",
                "html": "<p><strong>Development</strong> includes all changes from germination to senescence — broadly <strong>growth + differentiation</strong>. <strong>Plasticity</strong> allows different pathways in response to environment (e.g. <strong>heterophylly</strong> in cotton, coriander, larkspur; buttercup leaves differ in air vs water). Intrinsic factors include <strong>plant growth regulators</strong>; extrinsic include light, temperature, water, nutrition.</p>",
            },
            {
                "id": "pgd-pgr-overview",
                "level": 2,
                "heading": "7. Plant growth regulators — overview",
                "html": "<p><strong>PGRs (phytohormones)</strong> are small molecules: auxins (indole compounds), gibberellins (terpenes), cytokinins (adenine derivatives), ABA (carotenoid derivative), ethylene (gas). Promoters (auxin, GA, cytokinin) stimulate division/enlargement/flowering; inhibitors (ABA, ethylene) regulate dormancy, abscission, stress. Discovery milestones: Darwin (phototropism/coleoptile tip), Went (auxin), Kurosawa (gibberellin), Skoog/Miller (kinetin), Cousins (ethylene).</p>",
            },
            {
                "id": "pgd-auxins",
                "level": 2,
                "heading": "8. Auxins",
                "html": "<p>Natural: <strong>IAA, IBA</strong>; synthetic: <strong>NAA, 2,4-D</strong>. Synthesised at shoot/root apices. Effects: cell elongation, <strong>apical dominance</strong> (removal of shoot tip → lateral buds grow — used in tea hedges), rooting of cuttings, <strong>parthenocarpy</strong> (tomato), prevent early fruit/leaf drop, promote abscission of older leaves, xylem differentiation, <strong>herbicide</strong> (2,4-D kills dicot weeds, not mature monocots). Highest auxin concentration in <strong>growing tips</strong>.</p>",
            },
            {
                "id": "pgd-gibberellins",
                "level": 2,
                "heading": "9. Gibberellins",
                "html": "<p>Over 100 GAs (GA₁, GA₃…); <strong>GA₃</strong> most studied; all acidic. Effects: stem/axis elongation (grape stalks, <strong>sugarcane yield</strong> ↑ ~20 t/acre), <strong>bolting</strong> in rosette plants (beet, cabbage), overcome seed dormancy, delay senescence, speed up malting in brewing, hasten maturity of conifers, elongate apple fruits. ABA is often antagonistic to GA.</p>",
            },
            {
                "id": "pgd-cytokinins",
                "level": 2,
                "heading": "10. Cytokinins",
                "html": "<p>Discovered as <strong>kinetin</strong> from herring sperm DNA; natural forms include <strong>zeatin</strong> (corn kernels, coconut milk). Promote <strong>cytokinesis</strong>, new leaves, chloroplast development, lateral shoot growth, adventitious buds; <strong>overcome apical dominance</strong>; <strong>delay leaf senescence</strong> via nutrient mobilisation. Used in tissue culture with auxin.</p>",
            },
            {
                "id": "pgd-ethylene",
                "level": 2,
                "heading": "11. Ethylene",
                "html": "<p>Gaseous PGR from ripening/senescing tissues. Promotes <strong>fruit ripening</strong> (respiratory climacteric), senescence and abscission, breaks seed/bud dormancy, horizontal growth of seedlings, <strong>root hair formation</strong> (increases absorption surface), flowering in mango/pineapple. Commercial source: <strong>ethephon</strong>. Ripe fruit releases ethylene → hastens ripening of nearby unripe fruit.</p>",
            },
            {
                "id": "pgd-aba",
                "level": 2,
                "heading": "12. Abscisic acid (ABA)",
                "html": "<p>Growth inhibitor; discovered as inhibitor-B/abscission II/dormin. <strong>Stress hormone</strong> — stimulates <strong>stomatal closure</strong>, induces seed dormancy (withstands desiccation), promotes abscission, inhibits germination. Seed dormancy is largely due to ABA. Antagonistic to gibberellins in many processes.</p>",
            },
            {
                "id": "pgd-photoperiod",
                "level": 2,
                "heading": "13. Photoperiodism & vernalisation",
                "html": "<p><strong>Photoperiodism</strong> (Garner &amp; Allard) — effect of day/night length on flowering. <strong>Short-day plants</strong> flower when day length &lt; critical period (uninterrupted long night); <strong>long-day plants</strong> when day &gt; critical; <strong>day-neutral</strong> (tomato, maize) flower in any photoperiod. Perceived in <strong>leaves</strong> via <strong>phytochrome</strong> (chromoprotein; P<sub>R</sub> ⇌ P<sub>FR</sub>). <strong>Vernalisation</strong> — low-temperature treatment promoting flowering. A <strong>defoliated plant</strong> cannot respond to photoperiod.</p>",
            },
            {
                "id": "pgd-tropisms",
                "level": 2,
                "heading": "14. Plant movements & seed dormancy",
                "html": "<p><strong>Phototropism</strong> — growth toward light (Darwin coleoptile experiments). <strong>Thigmotropism</strong> — coiling of pea tendrils around support. <strong>Seed dormancy</strong> — viable seeds fail to germinate despite favourable conditions (hard/impermeable seed coat, ABA); overcome by <strong>scarification</strong> or GA treatment. Germination requires favourable temperature, water, oxygen.</p>",
            },
        ],
    },
    {
        "id": "bio11-ch-digestion",
        "class": 11,
        "chapterNo": 16,
        "title": "Digestion and Absorption",
        "topic": "Digestion and Absorption",
        "intro": "NCERT Class XI Chapter 16: the human alimentary canal, digestion of carbohydrates, proteins and fats, the role of liver, pancreas and intestinal juice, absorption in the small intestine and assimilation of nutrients.",
        "sections": [
            {
                "id": "da-overview",
                "level": 2,
                "heading": "1. Digestion — overview & alimentary canal",
                "html": "<p><strong>Digestion</strong> converts complex food into simple absorbable forms. The <strong>alimentary canal</strong> is a continuous muscular tube: mouth → buccal cavity → pharynx → oesophagus → stomach → small intestine → large intestine → rectum → <strong>anus</strong> (posterior opening). Wall layers: <strong>mucosa, submucosa, muscularis, serosa</strong>. The canal and associated glands (salivary, liver, pancreas) form the digestive system.</p>",
            },
            {
                "id": "da-mouth",
                "level": 2,
                "heading": "2. Buccal cavity & teeth",
                "html": "<p>The mouth has teeth, tongue and salivary glands. Teeth cut and masticate food; <strong>enamel</strong> is the hardest substance in the vertebrate body. Normal adult human <strong>dental formula</strong>: I 2/2, C 1/1, PM 2/2, M 3/3 (2123/2123). Saliva contains <strong>salivary amylase (ptyalin)</strong> — begins starch digestion (~30% hydrolysed in mouth); lysozyme acts antibacterial.</p>",
            },
            {
                "id": "da-pharynx",
                "level": 2,
                "heading": "3. Pharynx & oesophagus",
                "html": "<p>The <strong>pharynx</strong> is the common passage for food and air; the glottis (respiratory) and gullet (oesophageal opening) are guarded during swallowing. The <strong>oesophagus</strong> conducts food to the stomach by <strong>peristalsis</strong>. No digestion occurs here.</p>",
            },
            {
                "id": "da-stomach",
                "level": 2,
                "heading": "4. Stomach & gastric digestion",
                "html": "<p>J-shaped expandable organ. <strong>Gastric glands</strong> secrete HCl, pepsinogen, mucus, intrinsic factor. <strong>Parietal (oxyntic) cells</strong> → HCl; <strong>chief (peptic) cells</strong> → pepsinogen (activated to pepsin by HCl). HCl kills bacteria, acidifies food, activates pepsin. Mucus and <strong>bicarbonate</strong> protect the mucosa from concentrated HCl. <strong>Gastrin</strong> stimulates gastric secretion; <strong>enterogastrone</strong> inhibits it when chyme enters duodenum.</p>",
            },
            {
                "id": "da-liver-bile",
                "level": 2,
                "heading": "5. Liver, gall bladder & bile",
                "html": "<p>The <strong>liver</strong> is the largest gland; hepatic cells secrete <strong>bile</strong> stored in the <strong>gall bladder</strong>. Bile has <strong>bile salts, bile pigments</strong> (bilirubin/biliverdin — give yellow colour to stools in breast-fed infants) and <strong>no digestive enzymes</strong>. Bile <strong>emulsifies fats</strong> (increases surface area for lipase action) and neutralises acidic chyme. Bile juice is essential for fat digestion.</p>",
            },
            {
                "id": "da-pancreas",
                "level": 2,
                "heading": "6. Pancreas & pancreatic juice",
                "html": "<p>Exocrine pancreas secretes <strong>pancreatic juice</strong> into the duodenum via the pancreatic duct. Contains <strong>trypsinogen, chymotrypsinogen, procarboxypeptidase, pancreatic amylase, lipase, nucleases</strong>. <strong>Enterokinase</strong> of intestinal juice activates trypsinogen → trypsin (which activates other zymogens). Pancreatic juice is alkaline (HCO₃⁻).</p>",
            },
            {
                "id": "da-small-intestine",
                "level": 2,
                "heading": "7. Small intestine — structure",
                "html": "<p>Longest part of the alimentary canal (duodenum, jejunum, ileum). Inner surface has <strong>circular folds, villi and microvilli</strong> to increase absorption area. <strong>Crypts of Lieberkühn</strong> (simple tubular glands) secrete intestinal juice. Brunner's glands (duodenum) secrete alkaline mucus. The ileum is the main site of <strong>absorption</strong> and completion of digestion.</p>",
            },
            {
                "id": "da-intestinal-juice",
                "level": 2,
                "heading": "8. Succus entericus (intestinal juice)",
                "html": "<p><strong>Succus entericus</strong> contains many enzymes: <strong>enterokinase, aminopeptidases, dipeptidases, maltase, lactase, sucrase, lipase, nucleotidases</strong>. <strong>Carboxypeptidase</strong> requires <strong>zinc</strong>. Final digestion of peptides, disaccharides and nucleotides occurs here. Nucleases are present in pancreatic juice, not typically listed as absent from succus entericus in the same way.</p>",
            },
            {
                "id": "da-digestion",
                "level": 2,
                "heading": "9. Digestion of biomolecules",
                "html": "<ul><li><strong>Carbohydrates</strong>: starch → maltose (salivary &amp; pancreatic amylase) → glucose (disaccharidases).</li><li><strong>Proteins</strong>: pepsin in stomach → peptides; trypsin/chymotrypsin in intestine → smaller peptides → amino acids (peptidases).</li><li><strong>Fats</strong>: emulsified by bile → digested by lipase to fatty acids + monoglycerides.</li><li><strong>Nucleic acids</strong>: pancreatic nucleases → nucleotides → nucleosides/nitrogenous bases.</li></ul>",
            },
            {
                "id": "da-absorption",
                "level": 2,
                "heading": "10. Absorption & transport",
                "html": "<p><strong>Absorption</strong> — end products pass through intestinal mucosa into blood/lymph. Monosaccharides, amino acids, Na⁺ and other electrolytes via <strong>active transport</strong>; fatty acids and glycerol → chylomicrons → <strong>lymph (lacteals)</strong>. Water moves by osmosis following solute absorption. Fat-soluble vitamins (A, D, E, K) with fats; water-soluble via blood. <strong>Vitamin B₁₂</strong> richest in liver/Spirulina; some B vitamins synthesised by gut bacteria.</p>",
            },
            {
                "id": "da-large-intestine",
                "level": 2,
                "heading": "11. Large intestine & egestion",
                "html": "<p>Colon reabsorbs water and electrolytes; hosts beneficial bacteria (vitamin synthesis, gas production). Faeces consist of undigested residue, bacteria, bile pigments. <strong>Appendix</strong> is a vestigial lymphoid organ. Parasites of intestine include tapeworm, roundworm, pinworm.</p>",
            },
        ],
    },
]

# ── Classification rules (most specific first) ─────────────────────────────────

RULESETS: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "bio11-ch-transport": (
        "tp-overview",
        [
            ("tp-phloem", r"phloem|sieve tube|sieve tube member|companion cell|p[\-\s]?protein|mass.?flow|pressure.?flow|source.{0,20}sink|sink.{0,20}source|translocation.{0,15}sucrose|sucrose.{0,20}transport|florigen"),
            ("tp-root-pressure", r"root pressure|guttation|hydathode"),
            ("tp-transpiration", r"transpir|stomata|stomatal|guard cell|cuticular|lenticel|wilting|humid|transpiration pull"),
            ("tp-xylem", r"xylem|cohesion|adhesion|tension|water column|ascent of sap|transpiration pull.{0,30}root pressure|pulling and pushing"),
            ("tp-imbibition", r"imbibition|swelling.{0,20}seed|mustard seed"),
            ("tp-water-potential", r"water potential|ψ|psi|solute potential|pressure potential|pure water.{0,30}zero|osmotic pressure|turgor"),
            ("tp-pathways", r"apoplast|symplast|casparian|endoderm"),
            ("tp-active-transport", r"active transport|against.{0,15}gradient|atp.{0,20}transport|mineral.{0,20}uptake|carrier protein|channel protein|facilitated diffusion"),
            ("tp-diffusion-osmosis", r"diffusion|osmosis|hypotonic|hypertonic|isotonic|exosmosis|plasmolysis|semi.?permeable|permeable membrane|facilitated"),
        ],
    ),
    "bio11-ch-mineral": (
        "mn-overview",
        [
            ("mn-biological-fixation", r"nitrogenase|rhizobium|nodule|leg.?haemoglobin|leghemoglobin|biological nitrogen|azotobacter|anabaena|frankia|symbiotic.{0,15}fix|free.?living.{0,15}fix|ammonia.{0,20}first stable|fixation.{0,15}legumin"),
            ("mn-nitrogen-cycle", r"nitrogen cycle|nitrification|denitrification|ammonification|nitrobacter|nitrosomonas|industrial nitrogen|haber"),
            ("mn-hydroponics", r"hydroponic|solution culture|von sachs"),
            ("mn-special-modes", r"insectivor|pitcher plant|venus|mycorrhiz|dodder|parasitic.{0,15}plant|carnivorous"),
            ("mn-micronutrients", r"micronutrient|micro.?nutrient|trace element|iron|manganese|mn |zinc|copper|molybdenum|boron|chlorine|nickel|gray spot|grey spot|rosette|little leaf|interveinal|zn |cu |mo |fe |cl "),
            ("mn-macronutrients", r"macronutrient|macro.?nutrient|nitrogen|phosphorus|potassium|calcium|magnesium|sulphur|sulfur|chlorosis|nitrification|phosphorus|npk|phosphate"),
            ("mn-absorption", r"absorption.{0,15}mineral|anaerobic.{0,20}mineral|soil.{0,20}mineral|toxic|remobil|immobil|calcium.{0,20}permeab|critical concentration|deficien"),
            ("mn-criteria", r"criteria|essential element|arnon|stout|critical concentration|17 essential"),
        ],
    ),
    "bio11-ch13": (
        "pgd-overview",
        [
            ("pgd-photoperiod", r"photoperiod|phytochrome|short day|long day|day.?neutral|garner|allard|vernalisation|vernalization|dark period.{0,20}flower|critical day|uninterrupted.{0,10}night|defoliated"),
            ("pgd-tropisms", r"thigmotrop|phototrop|geotrop|nastic|tendril|coleoptile|darwin.{0,20}light|seed dormanc|germination|scarification"),
            ("pgd-ethylene", r"ethylene|ethephon|climacteric|ripening|ripen"),
            ("pgd-aba", r"abscisic|aba |dormin|abscission ii|inhibitor.?b|stress hormone|stomatal closure"),
            ("pgd-cytokinins", r"cytokinin|kinetin|zeatin|cytokinesis|cell division.{0,15}promot"),
            ("pgd-gibberellins", r"gibberell|ga3|ga₃|bolting|bakanae|kurosawa|malting|sugarcane"),
            ("pgd-auxins", r"auxin|iaa|iba|2,4.?d|naphthalene acetic|apical dominance|decapitat|parthenocarp|went "),
            ("pgd-pgr-overview", r"plant growth regulator|pgr|phytohormone|plant hormone|growth promoter|growth inhibitor|skook|miller|cousins"),
            ("pgd-differentiation", r"differentiat|dedifferentiat|redifferentiat|tracheary|lignified|protoplasm loss"),
            ("pgd-growth-rates", r"arithmetic growth|geometric growth|sigmoid|s.?curve|lag phase|log phase|relative growth|absolute growth|growth rate|lt.?=.?l0|exponential"),
            ("pgd-phases", r"meristematic phase|elongation phase|maturation phase|zone of elongation|parallel line"),
            ("pgd-meristems", r"meristem|apical meristem|cambium|indeterminate|open form|secondary growth|intercalary"),
            ("pgd-development", r"plasticity|heterophyl|development|juvenile.{0,10}leaf|buttercup|larkspur"),
        ],
    ),
    "bio11-ch-digestion": (
        "da-overview",
        [
            ("da-large-intestine", r"large intestine|colon|rectum|appendix|faeces|feces|egestion|tapeworm|roundworm|pinworm|parasite.{0,15}intestin"),
            ("da-absorption", r"absorption|absorbed|lacteal|chylomicron|vitamin b.?12|vitamin.{0,10}synthes|spirulina|goat.?s liver|enterogastrone|gastrin|assimilat"),
            ("da-intestinal-juice", r"succus entericus|intestinal juice|enterokinase|carboxypeptidase|dipeptidase|maltase|lactase|sucrase|nucleotidase|crypts of lieberk|lieberkühn|lieberkuhn"),
            ("da-digestion", r"digestion of|starch|pepsin|trypsin|chymotrypsin|lipase|emulsif|ptyalin|amylase|nuclease|dna.{0,15}digest|protein digestion|fat digestion|boiled potato"),
            ("da-pancreas", r"pancrea|pancreatic|trypsinogen|chymotrypsinogen|procarboxypeptidase"),
            ("da-liver-bile", r"\bbile\b|liver|hepatic|gall bladder|gallbladder|bilirubin|biliverdin|emulsif"),
            ("da-stomach", r"stomach|gastric|pepsin|hcl|parietal|oxyntic|chief cell|peptic cell|mucosa.{0,15}protect|gastric juice|chyme"),
            ("da-pharynx", r"pharynx|oesophagus|esophagus|peristalsis|glottis|gullet"),
            ("da-mouth", r"\bteeth\b|tooth|dental formula|enamel|buccal|salivary|ptyalin|mouth|incisor|molar|canine|premolar"),
            ("da-small-intestine", r"small intestine|duodenum|jejunum|ileum|villi|microvilli|brunner"),
        ],
    ),
}


def merge() -> None:
    notes = json.loads((ROOT / "notes.json").read_text(encoding="utf-8"))
    note_links = json.loads((ROOT / "note_links.json").read_text(encoding="utf-8"))

    for chapter in CHAPTERS:
        cid = chapter["id"]
        topic = chapter["topic"]
        default, ruleset = RULESETS[cid]
        questions = load_bank(topic)
        expected = {
            "bio11-ch-transport": 238,
            "bio11-ch-mineral": 187,
            "bio11-ch13": 514,
            "bio11-ch-digestion": 271,
        }[cid]
        if len(questions) != expected:
            print(f"WARN {cid}: bank count {len(questions)} != expected {expected}")

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
