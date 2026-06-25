#!/usr/bin/env python3
"""Add bio11-ch18 and bio11-ch19 chapter notes + MCQ links."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from note_pipeline import (  # noqa: E402
    build_links,
    load_bank,
    print_distribution,
    upsert_chapter_links,
    upsert_chapter_notes,
    verify_all,
)

CH18 = {
    "id": "bio11-ch18",
    "class": 11,
    "chapterNo": 18,
    "title": "Neural Control and Co-ordination",
    "topic": "Neural Control and Co-ordination",
    "intro": (
        "NCERT Class XI Chapter 18: neural coordination — the human nervous system "
        "(CNS and PNS), neuron structure, resting and action potentials, synaptic "
        "transmission, and the forebrain, midbrain and hindbrain."
    ),
    "sections": [
        {
            "id": "nc-overview",
            "level": 2,
            "heading": "1. Neural system & coordination",
            "html": (
                "<p>Organs must be <strong>coordinated</strong> so their activities complement "
                "one another (e.g. during exercise: muscles, lungs, heart and kidneys work "
                "together). The <strong>neural system</strong> gives rapid point-to-point "
                "connections; the <strong>endocrine system</strong> gives slower chemical "
                "integration via hormones. Neurons are highly specialised cells that detect, "
                "receive and transmit stimuli. Organisation is simple in lower invertebrates "
                "(e.g. <em>Hydra</em> — a nerve net); better in insects (brain + ganglia); most "
                "developed in vertebrates.</p>"
            ),
        },
        {
            "id": "nc-human-system",
            "level": 2,
            "heading": "2. Human neural system (CNS & PNS)",
            "html": (
                "<p><strong>CNS</strong> — brain + spinal cord (information processing and "
                "control). <strong>PNS</strong> — all nerves linked to the CNS. Nerve fibres: "
                "<strong>afferent</strong> (sensory → CNS) and <strong>efferent</strong> "
                "(CNS → effectors). PNS divisions: <strong>somatic</strong> (to skeletal "
                "muscles) and <strong>autonomic</strong> (to involuntary organs/smooth muscle) "
                "— further split into <strong>sympathetic</strong> and "
                "<strong>parasympathetic</strong>. The <strong>visceral nervous system</strong> "
                "is the PNS component linking viscera and CNS.</p>"
            ),
        },
        {
            "id": "nc-neuron-structure",
            "level": 2,
            "heading": "3. Neuron — structure & types",
            "html": (
                "<p>A neuron has a <strong>cell body</strong> (with <strong>Nissl's "
                "granules</strong>), <strong>dendrites</strong> (conduct impulses toward the "
                "cell body) and an <strong>axon</strong> (conducts away; ends in synaptic "
                "knobs with neurotransmitter vesicles). Types by processes: "
                "<strong>multipolar</strong> (one axon, ≥2 dendrites — cerebral cortex), "
                "<strong>bipolar</strong> (one each — retina), <strong>unipolar</strong> "
                "(one process — embryonic). Axons may be <strong>myelinated</strong> or "
                "<strong>non-myelinated</strong>.</p>"
            ),
        },
        {
            "id": "nc-myelination",
            "level": 2,
            "heading": "4. Myelinated & non-myelinated fibres",
            "html": (
                "<p><strong>Myelinated</strong> fibres are wrapped by <strong>Schwann "
                "cells</strong> forming a myelin sheath; gaps between sheaths are "
                "<strong>nodes of Ranvier</strong> (saltatory conduction). Found in spinal "
                "and cranial nerves. <strong>Non-myelinated</strong> fibres have Schwann "
                "cells without a myelin sheath — common in autonomic and somatic systems. "
                "Myelination greatly speeds impulse conduction.</p>"
            ),
        },
        {
            "id": "nc-membrane-potential",
            "level": 2,
            "heading": "5. Resting & action potentials",
            "html": (
                "<p>At rest the axonal membrane is more permeable to <strong>K⁺</strong> than "
                "<strong>Na⁺</strong>; the <strong>Na⁺/K⁺ pump</strong> (3 Na⁺ out, 2 K⁺ in) "
                "maintains ionic gradients — outer surface positive, inner negative → "
                "<strong>resting potential</strong> (~−70 mV). A stimulus opens Na⁺ channels "
                "→ rapid Na⁺ influx → <strong>depolarisation</strong> → "
                "<strong>action potential</strong> (nerve impulse). Local currents depolarise "
                "adjacent regions; K⁺ efflux restores resting potential "
                "(<strong>repolarisation</strong>). Includes absolute/relative refractory "
                "periods.</p>"
            ),
        },
        {
            "id": "nc-synapse",
            "level": 2,
            "heading": "6. Synaptic transmission",
            "html": (
                "<p>Impulses pass between neurons at <strong>synapses</strong> (pre- and "
                "post-synaptic membranes, optionally separated by a <strong>synaptic "
                "cleft</strong>). <strong>Electrical synapses</strong> — membranes very close, "
                "direct current flow; always faster but rare. <strong>Chemical synapses</strong> "
                "— neurotransmitters released from synaptic vesicles bind post-synaptic "
                "receptors, opening ion channels → excitatory or inhibitory post-synaptic "
                "potentials.</p>"
            ),
        },
        {
            "id": "nc-brain-overview",
            "level": 2,
            "heading": "7. Brain — protection & major divisions",
            "html": (
                "<p>The brain is protected by the skull and <strong>cranial meninges</strong>: "
                "outer <strong>dura mater</strong>, thin <strong>arachnoid</strong>, inner "
                "<strong>pia mater</strong> (on brain tissue). Three major parts: "
                "<strong>forebrain</strong>, <strong>midbrain</strong>, "
                "<strong>hindbrain</strong>. The <strong>brain stem</strong> (midbrain + pons + "
                "medulla) connects brain to spinal cord. Controls voluntary movement, balance, "
                "vital organs, thermoregulation, hunger/thirst, circadian rhythms, endocrine "
                "glands, behaviour, vision, hearing, speech, memory and emotions.</p>"
            ),
        },
        {
            "id": "nc-forebrain",
            "level": 2,
            "heading": "8. Forebrain",
            "html": (
                "<p>Comprises <strong>cerebrum</strong>, <strong>thalamus</strong> and "
                "<strong>hypothalamus</strong>. Cerebrum — two hemispheres linked by "
                "<strong>corpus callosum</strong>; outer <strong>cerebral cortex</strong> "
                "(grey matter — motor, sensory and association areas) over inner white matter "
                "(myelinated tracts). Thalamus — major sensory/motor relay. Hypothalamus — "
                "body temperature, eating/drinking, neurosecretory cells releasing "
                "hypothalamic hormones. <strong>Limbic system</strong> (with hypothalamus) — "
                "emotion, motivation, sexual behaviour.</p>"
            ),
        },
        {
            "id": "nc-midbrain-hindbrain",
            "level": 2,
            "heading": "9. Midbrain & hindbrain",
            "html": (
                "<p><strong>Midbrain</strong> — between thalamus/hypothalamus and pons; "
                "<strong>cerebral aqueduct</strong> passes through it; dorsal "
                "<strong>corpora quadrigemina</strong> (four lobes) integrate visual, tactile "
                "and auditory inputs. <strong>Hindbrain</strong> — <strong>pons</strong> "
                "(fibre tracts linking brain regions), <strong>cerebellum</strong> (convoluted "
                "surface; coordinates balance/movement using vestibular and auditory input) and "
                "<strong>medulla oblongata</strong> (connected to spinal cord; centres for "
                "respiration, cardiovascular reflexes and gastric secretions).</p>"
            ),
        },
        {
            "id": "nc-reflex",
            "level": 2,
            "heading": "10. Reflex action",
            "html": (
                "<p>A <strong>reflex</strong> is a rapid, involuntary response to a stimulus "
                "via a reflex arc (receptor → sensory neuron → integration centre in CNS → "
                "motor neuron → effector). Spinal reflexes (e.g. knee-jerk, withdrawal reflex) "
                "bypass conscious brain processing for speed. The simplest reflex arc involves "
                "one sensory and one motor neuron (monosynaptic).</p>"
            ),
        },
        {
            "id": "nc-eye",
            "level": 2,
            "heading": "11. Eye & vision",
            "html": (
                "<p>The eyeball wall layers (inside → out): retina, choroid, sclera. "
                "<strong>Retina</strong> has <strong>rods</strong> (dim light) and "
                "<strong>cones</strong> (colour/bright light); contains bipolar neurons. "
                "<strong>Iris</strong> controls pupil diameter; <strong>lens</strong> focuses "
                "light (held by suspensory ligament/Zonule of Zinn). <strong>Rhodopsin</strong> "
                "(visual purple) in rods needs vitamin A. <strong>Cornea</strong> and lens "
                "refract light; vitreous chamber filled with vitreous humour.</p>"
            ),
        },
        {
            "id": "nc-ear",
            "level": 2,
            "heading": "12. Ear & hearing",
            "html": (
                "<p>Ear: <strong>outer</strong> (pinna, ear canal, tympanic membrane), "
                "<strong>middle</strong> (ossicles — malleus, incus, stapes linking tympanum "
                "to oval window) and <strong>inner</strong> (bony labyrinth with perilymph; "
                "membranous labyrinth with endolymph). <strong>Cochlea</strong> — organ of Corti "
                "and sound reception. <strong>Vestibular apparatus</strong> — semicircular "
                "canals (angular acceleration) and utricle/saccule with <strong>otolith "
                "organs/maculae</strong> (gravity/linear acceleration). Scala vestibuli and "
                "scala tympani filled with perilymph.</p>"
            ),
        },
    ],
}

CH19 = {
    "id": "bio11-ch19",
    "class": 11,
    "chapterNo": 19,
    "title": "Chemical Coordination and Integration",
    "topic": "Co-ordination and Integration",
    "intro": (
        "NCERT Class XI Chapter 19: chemical coordination through hormones — the human "
        "endocrine glands (hypothalamus–pituitary axis, thyroid, adrenals, pancreas, gonads "
        "and others), hormones of heart/kidney/GI tract, and mechanisms of hormone action."
    ),
    "sections": [
        {
            "id": "cc-overview",
            "level": 2,
            "heading": "1. Endocrine glands & hormones",
            "html": (
                "<p><strong>Endocrine glands</strong> are ductless; their secretions "
                "(<strong>hormones</strong>) are non-nutrient intercellular messengers produced "
                "in trace amounts. Contrast <strong>exocrine glands</strong> (with ducts). The "
                "neural system gives fast, short-lived coordination; hormones give slower, "
                "sustained regulation. Major endocrine organs: hypothalamus, pituitary, pineal, "
                "thyroid, parathyroid, thymus, adrenal, pancreas and gonads; heart, kidney and "
                "GI tract also secrete hormones.</p>"
            ),
        },
        {
            "id": "cc-hypothalamus-pituitary",
            "level": 2,
            "heading": "2. Hypothalamus & pituitary",
            "html": (
                "<p><strong>Hypothalamus</strong> neurosecretory nuclei release "
                "<strong>releasing</strong> and <strong>inhibiting</strong> hormones (via "
                "hypothalamo-hypophyseal portal system) to control the anterior pituitary; "
                "directly regulates posterior pituitary. <strong>Pituitary</strong> in sella "
                "turcica: <strong>adenohypophysis</strong> (pars distalis + pars intermedia) "
                "and <strong>neurohypophysis</strong> (pars nervosa). Anterior hormones: "
                "GH, PRL, TSH, ACTH, LH, FSH, MSH. Posterior stores/releases "
                "<strong>oxytocin</strong> and <strong>vasopressin (ADH)</strong> made in "
                "hypothalamus. GH excess → gigantism/acromegaly; deficiency → dwarfism. ADH "
                "deficiency → diabetes insipidus.</p>"
            ),
        },
        {
            "id": "cc-pineal-thyroid",
            "level": 2,
            "heading": "3. Pineal & thyroid glands",
            "html": (
                "<p><strong>Pineal</strong> (dorsal forebrain) secretes <strong>melatonin</strong> "
                "— regulates circadian rhythms (sleep–wake, body temperature, menstrual cycle). "
                "<strong>Thyroid</strong> — two lobes + isthmus; follicles secrete "
                "<strong>T₃</strong> and <strong>T₄</strong> (need dietary iodine). Regulate "
                "BMR, growth/CNS development, erythropoiesis and carbohydrate/protein/fat "
                "metabolism. Also secretes <strong>thyrocalcitonin (TCT)</strong> lowering "
                "blood Ca²⁺. Iodine deficiency → goitre/cretinism; excess → hyperthyroidism "
                "(Graves'/exophthalmic goitre).</p>"
            ),
        },
        {
            "id": "cc-parathyroid-thymus",
            "level": 2,
            "heading": "4. Parathyroid & thymus",
            "html": (
                "<p><strong>Parathyroid</strong> (four glands on thyroid posterior) secretes "
                "<strong>PTH</strong> — raises blood Ca²⁺ via bone resorption, renal "
                "reabsorption and intestinal absorption (hypercalcemic; works with TCT). "
                "<strong>Thymus</strong> (behind sternum) secretes <strong>thymosins</strong> "
                "— T-lymphocyte differentiation (cell-mediated immunity) and antibody "
                "production (humoral immunity). Thymus degenerates with age → weaker immunity "
                "in the elderly.</p>"
            ),
        },
        {
            "id": "cc-adrenal",
            "level": 2,
            "heading": "5. Adrenal gland",
            "html": (
                "<p>One gland above each kidney. <strong>Adrenal medulla</strong> — "
                "<strong>adrenaline/epinephrine</strong> and "
                "<strong>noradrenaline/norepinephrine</strong> (catecholamines; emergency/"
                "fight-or-flight hormones: alertness, pupil dilation, sweating, ↑ heart rate/"
                "respiration, glycogenolysis). <strong>Adrenal cortex</strong> zones: "
                "zona glomerulosa (<strong>mineralocorticoids</strong> — aldosterone, Na⁺ "
                "reabsorption), zona fasciculata/reticularis "
                "(<strong>glucocorticoids</strong> — cortisol: gluconeogenesis, "
                "anti-inflammatory) plus small androgens. Cortex underproduction → "
                "Addison's disease.</p>"
            ),
        },
        {
            "id": "cc-pancreas",
            "level": 2,
            "heading": "6. Pancreas (endocrine)",
            "html": (
                "<p>Composite gland — exocrine (digestive enzymes) + endocrine "
                "<strong>Islets of Langerhans</strong> (α and β cells). "
                "<strong>Glucagon</strong> (α) — hyperglycemic: glycogenolysis and "
                "gluconeogenesis in liver. <strong>Insulin</strong> (β) — hypoglycemic: "
                "enhances glucose uptake/utilisation and glycogenesis in hepatocytes and "
                "adipocytes. Together maintain glucose homeostasis. Prolonged "
                "hyperglycemia → <strong>diabetes mellitus</strong> (treated with insulin).</p>"
            ),
        },
        {
            "id": "cc-gonads",
            "level": 2,
            "heading": "7. Testis & ovary",
            "html": (
                "<p><strong>Testis</strong> (scrotum) — Leydig cells secrete "
                "<strong>androgens/testosterone</strong>: male accessory sex organ "
                "development, secondary sexual characters, spermatogenesis, libido, anabolic "
                "effects. <strong>Ovary</strong> — growing follicles secrete "
                "<strong>estrogens</strong> (secondary sex characters, follicle growth, "
                "mammary development); post-ovulation <strong>corpus luteum</strong> secretes "
                "<strong>progesterone</strong> (pregnancy maintenance, mammary alveoli and "
                "milk secretion).</p>"
            ),
        },
        {
            "id": "cc-gi-heart-kidney",
            "level": 2,
            "heading": "8. Heart, kidney & GI hormones",
            "html": (
                "<p><strong>Heart</strong> atria — <strong>ANF</strong> (atrial natriuretic "
                "factor) lowers blood pressure (vasodilation). <strong>Kidney</strong> "
                "juxtaglomerular cells — <strong>erythropoietin</strong> stimulates RBC "
                "formation. <strong>GI tract</strong> endocrine cells: <strong>gastrin</strong> "
                "(HCl/pepsinogen), <strong>secretin</strong> (pancreatic H₂O/HCO₃⁻), "
                "<strong>CCK</strong> (pancreatic enzymes + bile), <strong>GIP</strong> "
                "(inhibits gastric secretion/motility).</p>"
            ),
        },
        {
            "id": "cc-mechanism",
            "level": 2,
            "heading": "9. Mechanism of hormone action",
            "html": (
                "<p>Hormones bind specific <strong>receptors</strong> on target cells. "
                "<strong>Membrane-bound receptors</strong> (peptide/protein hormones, "
                "catecholamines) generate <strong>second messengers</strong> (cAMP, IP₃, "
                "Ca²⁺). <strong>Intracellular/nuclear receptors</strong> (steroids, thyroid "
                "hormones) enter the cell and regulate gene expression. Hormone classes: "
                "peptides, steroids, iodothyronines and amino-acid derivatives (e.g. "
                "epinephrine). One receptor per hormone — high specificity.</p>"
            ),
        },
    ],
}

NC_RULES: list[tuple[str, str]] = [
    ("nc-ear", r"ear\b|tympanic|cochlea|vestibular|semicircular|scala vestibuli|scala tympani|reissner|organ of corti|auditory|hearing|eustachian|malleus|incus|stapes|oval window|round window|pinna|macula|otolith"),
    ("nc-eye", r"retina|rods|cones|cornea|iris|pupil|choroid|lens|eyeball|vision|optic|fovea|blind spot|sclera|rhodopsin|vitreous|suspensory ligament|zonule"),
    ("nc-reflex", r"reflex|knee jerk|withdrawal"),
    ("nc-forebrain", r"cerebr|cerebral|corpus callosum|limbic|thalamus|hypothalamus|association area|grey matter|white matter|forebrain|broca|parkinson|alzheimer|basal ganglia"),
    ("nc-midbrain-hindbrain", r"midbrain|hindbrain|pons|cerebell|medulla|corpora quadrigemina|brain stem|brainstem|regulation of respiration|cardiovascular reflex|gastric secretion"),
    ("nc-brain-overview", r"meninges|dura mater|arachnoid|pia mater|skull|cranial\b|brain\b|spinal cord|bowman.?s gland"),
    ("nc-synapse", r"synap|neurotransmitter|synaptic cleft|pre.?synaptic|post.?synaptic|electrical synap|chemical synap"),
    ("nc-membrane-potential", r"action potential|depolar|repolar|nerve impulse|impulse conduction|stimulus|resting potential|resting membrane|sodium.?potassium|na\+.?k\+|na/k pump|polarised|polarized|polarisation|polarization|membrane potential|neural membrane|refractory|axoplasm|intracellular cation|rapid na"),
    ("nc-myelination", r"myelin|schwann|nodes of ranvier|myelinated|non.?myelinated|unmyelinated"),
    ("nc-neuron-structure", r"dendrit|nissl|axon|multipolar|bipolar|unipolar|neuron|neurone|neurons|neurones|nerve fibre|nerve fiber"),
    ("nc-human-system", r"peripheral|afferent|efferent|somatic|autonomic|sympathetic|parasympathetic|cns|pns|cranial nerve|spinal nerve|visceral|central neural|peripheral neural"),
    ("nc-overview", r"hydra|invertebrate|neural system|neural coordination|co-ordination|coordination\b|endocrine system jointly|physical exercise|oxygen supply|two systems jointly|chemical integration"),
]

CC_RULES: list[tuple[str, str]] = [
    ("cc-mechanism", r"receptor|second messenger|membrane.?bound|intracellular receptor|steroid hormone|gene expression|cyclic amp|camp\b|mechanism of hormone|hormone.?receptor|act as secondary"),
    ("cc-gi-heart-kidney", r"gastrin|secretin|cholecystokinin|cck\b|gip|gastric inhibitory|atrial natriuretic|anf\b|erythropoietin|juxtaglomerular|gastrointestinal|g-i tract|gastric gland|bile juice"),
    ("cc-gonads", r"testis|testes|ovary|ovaries|androgen|testosterone|estrogen|oestrogen|progesterone|leydig|graafian|corpus luteum|spermatogenesis|mammary|seminiferous|accessory sex organ|epididymis|vas deferens"),
    ("cc-pancreas", r"pancrea|insulin|glucagon|islets of langerhans|diabetes mellitus|langerhans|hyperglycem|hypoglycem"),
    ("cc-adrenal", r"adrenal|epinephrine|adrenaline|norepinephrine|noradrenaline|catecholamine|cortisol|aldosterone|glucocorticoid|mineralocorticoid|addison|fight.?or.?flight|zona glomerulosa|zona fasciculata|\bcortex\b|medullary.? region"),
    ("cc-parathyroid-thymus", r"parathyroid|pth\b|thymus|thymosin|t-lymphocyte|cell.?mediated|humoral immunity|immune response|osteoporosis|calcium|ca\^{2\+}|ca2\+"),
    ("cc-pineal-thyroid", r"pineal|melatonin|thyroid|thyroxine|triiodothyronine|t3\b|t4\b|goitre|goiter|cretinism|graves|hyperthyroid|hypothyroid|thyrocalcitonin|calcitonin|iodine deficiency|stunted growth.*mental retardation"),
    ("cc-hypothalamus-pituitary", r"hypothalamus|pituitary|adenohypophysis|neurohypophysis|oxytocin|vasopressin|adh|antidiuretic|growth hormone|prolactin|tsh|acth|fsh|lh\b|gnrh|gonadotroph|acromegaly|gigantism|dwarfism|sella turcica|diabetes insipidus|pars distalis|pars nervosa|melanocyte stimulating|msh\b"),
    ("cc-overview", r"endocrine gland|ductless|hormone\b|hormones\b|exocrine|intercellular messenger|endocrine system|jointly coordinat|hormonal system|odorous secretion"),
]


def main() -> int:
    notes = json.loads((ROOT / "notes.json").read_text(encoding="utf-8"))
    note_links = json.loads((ROOT / "note_links.json").read_text(encoding="utf-8"))

    chapters = [
        (CH18, NC_RULES, "nc-overview"),
        (CH19, CC_RULES, "cc-overview"),
    ]

    for chapter, rules, default in chapters:
        questions = load_bank(chapter["topic"])
        expected = 415 if chapter["id"] == "bio11-ch18" else 456
        if len(questions) != expected:
            print(f"ERROR {chapter['id']}: expected {expected} MCQs, got {len(questions)}")
            return 1

        links = build_links(questions, rules, default)
        sec_ids = {s["id"] for s in chapter["sections"]}
        orphans = sorted({v for v in links.values() if v not in sec_ids})
        if orphans:
            print(f"ERROR {chapter['id']}: orphan sections {orphans}")
            return 1

        upsert_chapter_notes(notes, chapter)
        upsert_chapter_links(note_links, chapter["id"], chapter["topic"], links)

        print(f"\n{chapter['id']} — {len(questions)} MCQs, {len(chapter['sections'])} sections")
        print_distribution(links)

    (ROOT / "notes.json").write_text(
        json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "note_links.json").write_text(
        json.dumps(note_links, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    errs = verify_all()
    if errs:
        for e in errs:
            print(e)
        return 1

    print("\nVerification passed: 0 missing, 0 orphan for all linked chapters.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
