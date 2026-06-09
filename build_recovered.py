#!/usr/bin/env python3
"""Build recovered_questions.json from dropped Pearson items that were
completed by hand (Assertion-Reason answer keys + reconstructed text MCQs).
All entries are tagged "recovered" so admins can review/flag them in-app."""
import json, uuid
from pathlib import Path

ROOT = Path(__file__).parent
DROPPED = json.load(open("/tmp/pearson_dropped.json", encoding="utf-8"))

AR_OPTIONS = {
    "option_a": "Both assertion and reason are true and reason is the correct explanation of assertion.",
    "option_b": "Both assertion and reason are true but reason is not the correct explanation of assertion.",
    "option_c": "Assertion is true but reason is false.",
    "option_d": "Both assertion and reason are false.",
}

# Assertion-Reason answer keys, in the extraction order (Respiration 1-22,
# Neural 23-40, Biotech 41-59, Organisms 60).
AR_ANSWERS = list(
    "A A D A B B C A B B A A D A D A A C C B A A "  # Respiration in Plants (22)
    "B A A A A A A A A A A A C A A D C A "          # Neural Control (18)
    "B A C D A A A B D A A A A A A A C A A "        # Biotechnology Principles (19)
    "D".split()                                       # Organisms and Populations (1)
)

ar = [d for d in DROPPED
      if d["reason"] == "missing_answer" and d["stem"].strip().lower().startswith("assertion")]
assert len(ar) == len(AR_ANSWERS) == 60, (len(ar), len(AR_ANSWERS))

recovered = []
for raw, ans in zip(ar, AR_ANSWERS):
    recovered.append({
        "id": f"rec_ar_{uuid.uuid4().hex[:8]}",
        "question": raw["stem"],
        **AR_OPTIONS,
        "answer": ans,
        "explanation": "",
        "subject": "Biology",
        "topic": raw["chapter"],
        "subtopic": "Assertion-Reason",
        "tags": ["recovered"],
    })

# --- Reconstructed text MCQs (chapter, question, A, B, C, D, answer) ---
TEXT = [
 ("Biological Classification", "Contagium vivum fluidum was proposed by",
  "D. J. Ivanovsky", "M. W. Beijerinck", "W. M. Stanley", "Robert Hooke", "B"),
 ("Biological Classification",
  "Members of Phycomycetes are found in: i. Aquatic habitats  ii. On decaying wood  iii. Moist and damp places  iv. As obligate parasites on plants. Choose the correct option.",
  "i and iv only", "ii and iii only", "i, ii and iii only", "i, ii, iii and iv", "D"),
 ("Biological Classification", "A virus contains",
  "DNA only", "RNA only", "both DNA and RNA", "either DNA or RNA", "D"),
 ("Body Fluids and Circulation", "Which of the following statements is NOT true about the human heart?",
  "Heart is ectodermal in origin.",
  "In human beings the heart is situated in the thoracic cavity, in between the two lungs, slightly tilted to the left.",
  "The human heart is myogenic.",
  "Heart is protected by a double walled membranous bag (pericardium) with pericardial fluid.", "A"),
 ("Body Fluids and Circulation", "The tricuspid valve is present between the",
  "two atria", "two ventricles", "left atrium and left ventricle", "right atrium and right ventricle", "D"),
 ("Cell Cycle and Cell Division", "Crossing over takes place during which sub-stage of prophase I of meiosis?",
  "Leptotene", "Zygotene", "Pachytene", "Diplotene", "C"),
 ("Cell Cycle and Cell Division", "The cells that do not divide further enter the ___ phase from the G1 phase.",
  "S-phase", "G2-phase", "G0 (quiescent) phase", "M-phase", "C"),
 ("Co-ordination and Integration", "Which of the following statements is correct in relation to the endocrine system?",
  "Pituitary gland is the largest endocrine gland in the body.",
  "Organs in the body like gastrointestinal tract, heart, kidney and liver do not produce any hormones.",
  "Non-nutrient chemicals produced by the body in trace amount that act as intercellular messengers are known as hormones.",
  "Releasing and inhibitory hormones are produced by the pituitary gland.", "C"),
 ("Co-ordination and Integration",
  "The following are functions of which hormone? A. Anabolic effect on protein and carbohydrate metabolism  B. Influences male sexual behaviour (libido)  C. Stimulates spermatogenesis  D. Muscular growth, aggressiveness, low-pitched voice",
  "Oestrogen", "Progesterone", "Testosterone", "Relaxin", "C"),
 ("Digestion and Absorption", "Intestinal juice or succus entericus is formed by the secretion of",
  "goblet cells", "brush border cells lining the mucosa", "both goblet cells and brush border cells", "oxyntic cells", "C"),
 ("Digestion and Absorption", "Jaundice is a disorder of the",
  "excretory system", "skin and eyes", "digestive system", "circulatory system", "C"),
 ("Locomotion and Movement", "The sliding filament theory of muscle contraction can be best explained as",
  "when myofilaments slide past each other, the actin filaments shorten while myosin filaments do not shorten",
  "both actin and myosin filaments shorten during contraction",
  "actin and myosin filaments do not shorten but rather slide past each other",
  "when myofilaments slide past each other, the myosin filaments shorten while actin filaments do not shorten", "C"),
 ("Locomotion and Movement", "The number of bones in the vertebral column of an adult human is",
  "32", "26", "35", "33", "B"),
 ("Mineral Nutrition", "Which of the following pigments is essential for nitrogen fixation by leguminous plants?",
  "Anthocyanin", "Phycocyanin", "Phycoerythrin", "Leghaemoglobin", "D"),
 ("Photosynthesis in Higher Plants", "The classic bell-jar experiment (mouse, burning candle and a mint plant) was performed by",
  "Jan Ingenhousz", "Joseph Priestley", "Julius von Sachs", "Cornelius van Niel", "B"),
 ("Plant Growth and Development", "Who initiated the discovery of plant growth hormones through the study of phototropism in canary grass coleoptiles?",
  "Charles Darwin", "Francis Darwin", "Both Charles and Francis Darwin", "F. W. Went", "C"),
 ("Biotechnology Principles and Processes", "pBR322 is the most extensively studied",
  "plasmid DNA of E. coli", "bacteriophage", "rDNA", "cosmid", "A"),
 ("Evolution", "What was the most significant trend in the evolution of modern man (Homo sapiens) from his ancestors?",
  "shortening of the jaws", "walking upright (bipedalism)", "increasing cranial (brain) capacity", "loss of body hair", "C"),
 ("Human Health and Disease", "The mechanical carrier (vector) responsible for transmitting amoebiasis is the",
  "Entamoeba histolytica", "housefly", "mosquito", "Plasmodium vivax", "B"),
 ("Human Reproduction", "The uterus opens into the vagina through the",
  "ampulla", "fallopian tube", "cervix", "fimbriae", "C"),
 ("Principles of Inheritance and Variation", "A cross between an F1 individual and its homozygous recessive parent is called a",
  "back cross", "test cross", "out cross", "reciprocal cross", "B"),
 ("Reproduction in Organisms",
  "Consider these statements about sexual reproduction: i. It does not always require two individuals.  ii. It generally involves gametic fusion.  iii. Meiosis never occurs during sexual reproduction.  iv. External fertilization is a rule. Choose the correct statements.",
  "i and iv", "i and ii", "ii and iii", "iii and iv", "B"),
 ("Reproduction in Organisms",
  "Count the total number of organisms that are monoecious: Cucurbits, Coconut, Papaya, Date palm, Chara, Marchantia.",
  "1", "2", "3", "4", "C"),
]
for chapter, q, a, b, c, d, ans in TEXT:
    recovered.append({
        "id": f"rec_tx_{uuid.uuid4().hex[:8]}",
        "question": q,
        "option_a": a, "option_b": b, "option_c": c, "option_d": d,
        "answer": ans, "explanation": "",
        "subject": "Biology", "topic": chapter, "subtopic": "Recovered",
        "tags": ["recovered"],
    })

out = {"app": "NEET MCQ Practice", "version": 1,
       "questionCount": len(recovered), "questions": recovered}
(ROOT / "recovered_questions.json").write_text(
    json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"Wrote recovered_questions.json: {len(recovered)} questions "
      f"({len(ar)} Assertion-Reason + {len(TEXT)} reconstructed text)")
