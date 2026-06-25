#!/usr/bin/env python3
"""Merge bio11-ch14..ch17 notes + MCQ links into notes.json / note_links.json."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from note_pipeline import (
    ROOT,
    build_links,
    load_bank,
    upsert_chapter_links,
    upsert_chapter_notes,
    verify_all,
    print_distribution,
)

CHAPTERS = [
    {
        "id": "bio11-ch14",
        "class": 11,
        "chapterNo": 14,
        "title": "Breathing and Exchange of Gases",
        "topic": "Breathing and Exchange of Gases",
        "intro": "NCERT Class XI Chapter 14: respiratory organs, the mechanism of breathing, exchange and transport of O₂ and CO₂, regulation of respiration, and disorders of the respiratory system.",
        "default": "br-overview",
        "rules": [
            ("br-disorders", r"asthma|emphysema|occupational respiratory|silicosis|wheez|pneumoconiosis|byssinosis"),
            ("br-regulation", r"respiratory rhythm|pneumotaxic|chemosensitive|medulla.*respir|carotid.*(body|artery).*respir|aortic.*respir|regulation of respir|chemoreceptor.*respir|hypoxia|altitude.*respir|hill.*respir"),
            ("br-transport-co2", r"carbamino|bicarbonate.*co2|chloride shift|hco3|transport of co2|carbonic anhydrase|co2.*transport|co₂.*transport|haemoglobin.*co2|co2.*haemoglobin|co₂.*blood|carbon dioxide.*transport|hamburger"),
            ("br-transport-o2", r"oxyhaemoglobin|oxygen dissociation|dissociation curve|transport of o2|transport of oxygen|haemoglobin.*o2|oxygen.*haemoglobin|p50|bohr effect|percent saturation|sigmoid.*curve|2,3.?dpg|2,3.?bpg"),
            ("br-volumes", r"tidal volume|inspiratory reserve|expiratory reserve|residual volume|vital capacity|inspiratory capacity|expiratory capacity|functional residual|total lung capacity|spirometer|\bfrc\b|\berv\b|\birv\b|\btv\b|\btlc\b|\bvc\b|\bic\b|\bec\b|minute ventil|dead space"),
            ("br-exchange", r"partial pressure|p_o2|po2|pco2|p co2|diffusion membrane|solubility.*co2|alveolar.*exchange|exchange of gas|gradient.*alveol|thickness.*membrane.*diffus|fick"),
            ("br-mechanism", r"inspiration|expiration|diaphragm|intercostal|intrapulmonary|breathing involve|mechanism of breath|negative pressure.*lung|positive pressure.*lung|forced expir|forced inspir|abdominal muscle.*breath"),
            ("br-respiratory-organs", r"alveol|bronch|trachea|larynx|pleura|nostril|nasal|epiglottis|glottis|pharynx|conducting part|exchange part|respiratory organ|gill|tracheal tub|branchial|pulmonary respir|cutaneous respir|vocal cord|sound box|terminal bronchiole|pleural fluid"),
        ],
        "sections": [
            {
                "id": "br-overview",
                "level": 2,
                "heading": "1. Overview & steps of respiration",
                "html": "<p><strong>Breathing</strong> (pulmonary ventilation) is the exchange of atmospheric O₂ with alveolar CO₂. Respiration in animals involves: (i) <strong>breathing</strong> — inspiration and expiration; (ii) <strong>diffusion</strong> of O₂ and CO₂ across the alveolar membrane; (iii) <strong>transport</strong> of gases by blood; (iv) <strong>tissue exchange</strong>; (v) <strong>cellular respiration</strong> (Ch 12). Lower invertebrates exchange gases by simple diffusion; earthworms use the moist cuticle; insects use <strong>tracheae</strong>; aquatic forms use <strong>gills</strong>; terrestrial vertebrates use <strong>lungs</strong>. Amphibians also respire through moist skin (<strong>cutaneous respiration</strong>).</p>",
            },
            {
                "id": "br-respiratory-organs",
                "level": 2,
                "heading": "2. Human respiratory system",
                "html": "<p>Air enters through <strong>external nostrils → nasal chamber → pharynx → larynx</strong> (cartilaginous sound box; <strong>epiglottis</strong> covers glottis during swallowing) → <strong>trachea</strong> (incomplete cartilaginous rings) → right/left <strong>primary bronchi</strong> (at 5th thoracic vertebra) → secondary/tertiary bronchi → <strong>bronchioles</strong> → thin vascular <strong>alveoli</strong> (site of gas exchange). The <strong>conducting part</strong> (nostrils to terminal bronchioles) warms, humidifies and filters air; the <strong>exchange part</strong> (alveoli and ducts) is where diffusion occurs. Lungs lie in the airtight <strong>thoracic cavity</strong> (vertebral column, sternum, ribs, <strong>diaphragm</strong>), covered by double-layered <strong>pleura</strong> with pleural fluid reducing friction.</p>",
            },
            {
                "id": "br-mechanism",
                "level": 2,
                "heading": "3. Mechanism of breathing",
                "html": "<p><strong>Inspiration</strong>: contraction of the <strong>diaphragm</strong> (increases thoracic volume antero-posteriorly) and <strong>external intercostal muscles</strong> (lift ribs/sternum, dorso-ventral axis) → thoracic and pulmonary volume increase → <strong>intrapulmonary pressure falls below atmospheric</strong> → air flows in. <strong>Expiration</strong>: relaxation of diaphragm and intercostals → thoracic volume decreases → intrapulmonary pressure rises above atmospheric → air expelled. Forced breathing uses abdominal muscles. Average rate: <strong>12–16 breaths/min</strong>. A <strong>spirometer</strong> measures pulmonary volumes.</p>",
            },
            {
                "id": "br-volumes",
                "level": 2,
                "heading": "4. Respiratory volumes & capacities",
                "html": "<ul><li><strong>Tidal Volume (TV)</strong> — air inspired/expired per normal breath (~500 mL).</li><li><strong>IRV</strong> — extra inspired forcibly (~2500–3000 mL).</li><li><strong>ERV</strong> — extra expired forcibly (~1000–1100 mL).</li><li><strong>RV</strong> — air left after forced expiration (~1100–1200 mL).</li><li><strong>IC</strong> = TV + IRV; <strong>EC</strong> = TV + ERV.</li><li><strong>FRC</strong> = ERV + RV (after normal expiration).</li><li><strong>VC</strong> = ERV + TV + IRV (max breath in/out).</li><li><strong>TLC</strong> = VC + RV (total lung capacity).</li></ul>",
            },
            {
                "id": "br-exchange",
                "level": 2,
                "heading": "5. Exchange of gases",
                "html": "<p>Exchange at alveoli and tissues occurs by <strong>simple diffusion</strong> down partial-pressure gradients. <strong>Partial pressure</strong> (pO₂, pCO₂) drives movement: O₂ from alveoli (pO₂ ~104 mm Hg) to deoxygenated blood (~40) to tissues; CO₂ in the opposite direction. <strong>CO₂ is 20–25× more soluble</strong> than O₂, so more diffuses per unit gradient. The <strong>diffusion membrane</strong> = alveolar squamous epithelium + basement membrane + capillary endothelium (&lt;1 mm thick). Rate depends on gradient, solubility and membrane thickness.</p>",
            },
            {
                "id": "br-transport-o2",
                "level": 2,
                "heading": "6. Transport of oxygen",
                "html": "<p>~<strong>97% of O₂</strong> is carried by RBCs bound to <strong>haemoglobin</strong> (oxyhaemoglobin, reversible; max 4 O₂ per Hb); ~3% dissolved in plasma. Binding depends on pO₂, pCO₂, H⁺ and temperature. The <strong>oxygen dissociation curve</strong> (sigmoid) shows % saturation vs pO₂. At alveoli (high pO₂, low pCO₂, low H⁺, lower T) Hb loads O₂; at tissues (low pO₂, high pCO₂, high H⁺, higher T) O₂ is released. Every 100 mL oxygenated blood delivers ~<strong>5 mL O₂</strong> to tissues.</p>",
            },
            {
                "id": "br-transport-co2",
                "level": 2,
                "heading": "7. Transport of carbon dioxide",
                "html": "<p>CO₂ transport: ~<strong>70% as bicarbonate</strong> (HCO₃⁻, via <strong>carbonic anhydrase</strong>: CO₂ + H₂O ⇌ H₂CO₃ ⇌ H⁺ + HCO₃⁻); ~20–25% as <strong>carbamino-haemoglobin</strong>; ~7% dissolved. At tissues (high pCO₂) CO₂ enters blood → bicarbonate; at alveoli (low pCO₂) reaction reverses → CO₂ released. The <strong>chloride shift</strong> balances ionic charge. ~100 mL deoxygenated blood delivers ~<strong>4 mL CO₂</strong> to alveoli.</p>",
            },
            {
                "id": "br-regulation",
                "level": 2,
                "heading": "8. Regulation of respiration",
                "html": "<p>The <strong>respiratory rhythm centre</strong> in the medulla sets the basic breathing pattern. The <strong>pneumotaxic centre</strong> in the pons moderates it (shortens inspiration). A <strong>chemosensitive area</strong> near the rhythm centre responds to ↑CO₂ and H⁺. <strong>Peripheral chemoreceptors</strong> in the aortic arch and carotid artery also detect CO₂/H⁺ changes. O₂ plays a minor role in normal regulation. Neural control allows breathing to match tissue demands (e.g. exercise, altitude).</p>",
            },
            {
                "id": "br-disorders",
                "level": 2,
                "heading": "9. Disorders of the respiratory system",
                "html": "<ul><li><strong>Asthma</strong> — bronchi/bronchiole inflammation → wheezing, difficulty breathing.</li><li><strong>Emphysema</strong> — alveolar wall damage (often smoking) → reduced respiratory surface.</li><li><strong>Occupational respiratory disorders</strong> — dust (grinding, stone-breaking) → inflammation, fibrosis; workers need protective masks.</li></ul>",
            },
        ],
    },
    {
        "id": "bio11-ch15",
        "class": 11,
        "chapterNo": 15,
        "title": "Body Fluids and Circulation",
        "topic": "Body Fluids and Circulation",
        "intro": "NCERT Class XI Chapter 15: blood and lymph, circulatory pathways, the human heart and cardiac cycle, double circulation, regulation of cardiac activity, and disorders of the circulatory system.",
        "default": "bf-overview",
        "rules": [
            ("bf-disorders", r"hypertension|atherosclerosis|angina|heart failure|coronary artery|\bcad\b|myocardial infarction|140/90|congestive heart"),
            ("bf-regulation", r"sympathetic.*heart|parasympathetic.*heart|myogenic|cardiac.*regul|adrenal.*cardiac|vagus.*heart|autonomic.*heart|neural.*cardiac"),
            ("bf-ecg", r"\becg\b|electrocardiogram|p-wave|qrs complex|t-wave|pr interval|qt interval|depolarisation.*ventricle|repolarisation"),
            ("bf-double-circulation", r"double circul|pulmonary circul|systemic circul|hepatic portal|coronary circul|\baorta\b|vena cava|artery|vein|arteriole|venule|capillar|tunica intima|tunica media|tunica externa|blood vessel"),
            ("bf-cardiac-cycle", r"cardiac cycle|systole|diastole|stroke volume|cardiac output|\blub\b|\bdub\b|heart sound|atrial systole|ventricular systole|joint diastole|0\.8 second"),
            ("bf-human-heart", r"\bsan\b|\bavn\b|bundle of his|purkinje|pacemaker|sino.atrial|atrio.ventricular|tricuspid|bicuspid|mitral|semilunar|pericard|inter.atrial|inter.ventricular|auricle|ventricle.*heart|chamber.*heart|nodal tissue|autoexcit"),
            ("bf-circulatory-pathways", r"open circul|closed circul|2.chambered|3.chambered|4.chambered|single circul|incomplete double|fish.*heart|amphibian.*heart|reptile.*heart|mammal.*heart|bird.*heart|sinus.*circul"),
            ("bf-lymph", r"\blymph\b|interstitial fluid|tissue fluid|lacteal|lymphatic|lymphocyte.*lymph"),
            ("bf-coagulation", r"coagul|clot|fibrin|thrombin|prothrombin|thrombokinase|thromboplastin|calcium.*clot|haemostasis"),
            ("bf-blood-groups", r"\babo\b|rh factor|rhesus|universal donor|universal recipient|blood group|erythroblastosis|antigen.*rbc|anti.a|anti.b|\brh\+|\brh-"),
            ("bf-formed-elements", r"\brbc\b|\bwbc\b|erythrocyte|leucocyte|leukocyte|neutrophil|eosinophil|basophil|lymphocyte|monocyte|platelet|thrombocyte|megakaryocyte|granulocyte|agranulocyte|formed element|spleen.*rbc|graveyard"),
            ("bf-plasma", r"plasma|serum|albumin|globulin|fibrinogen"),
        ],
        "sections": [
            {
                "id": "bf-overview",
                "level": 2,
                "heading": "1. Overview — body fluids & circulation",
                "html": "<p>Higher animals transport nutrients, O₂ and wastes via specialised fluids. <strong>Blood</strong> is the main body fluid; <strong>lymph</strong> (tissue fluid) assists transport. Circulation may be <strong>open</strong> (arthropods, molluscs — blood into sinuses) or <strong>closed</strong> (annelids, chordates — blood in vessels). All vertebrates have a muscular chambered heart; pattern varies from 2-chambered (fish) to 4-chambered (birds, mammals).</p>",
            },
            {
                "id": "bf-plasma",
                "level": 2,
                "heading": "2. Plasma",
                "html": "<p><strong>Plasma</strong> is straw-coloured, viscous (~55% of blood); ~90–92% water, 6–8% proteins (<strong>fibrinogen</strong> — clotting; <strong>globulins</strong> — defence; <strong>albumin</strong> — osmotic balance). Contains minerals (Na⁺, Ca²⁺, Mg²⁺, HCO₃⁻, Cl⁻), glucose, amino acids, lipids and inactive clotting factors. <strong>Serum</strong> = plasma without clotting factors.</p>",
            },
            {
                "id": "bf-formed-elements",
                "level": 2,
                "heading": "3. Formed elements",
                "html": "<p>~45% of blood. <strong>RBCs (erythrocytes)</strong> — most abundant (~5–5.5 million/mm³), biconcave, enucleate in mammals, contain <strong>haemoglobin</strong> (12–16 g/100 mL), lifespan ~120 days, destroyed in spleen. <strong>WBCs (leucocytes)</strong> — ~6000–8000/mm³; <strong>granulocytes</strong> (neutrophils 60–65%, eosinophils 2–3%, basophils 0.5–1%) and <strong>agranulocytes</strong> (lymphocytes 20–25%, monocytes 6–8%). <strong>Platelets (thrombocytes)</strong> — 1.5–3.5 lakh/mm³, fragments from megakaryocytes, essential for clotting.</p>",
            },
            {
                "id": "bf-blood-groups",
                "level": 2,
                "heading": "4. Blood groups (ABO & Rh)",
                "html": "<p><strong>ABO</strong> — based on A/B antigens on RBCs and anti-A/anti-B antibodies in plasma: A (anti-B), B (anti-A), AB (no antibodies, <strong>universal recipient</strong>), O (anti-A,B; <strong>universal donor</strong>). <strong>Rh</strong> — Rh antigen on RBCs (~80% Rh⁺). Rh⁻ exposed to Rh⁺ blood forms anti-Rh antibodies. <strong>Erythroblastosis foetalis</strong> — Rh⁻ mother, Rh⁺ foetus in subsequent pregnancies; prevented by anti-Rh after first delivery.</p>",
            },
            {
                "id": "bf-coagulation",
                "level": 2,
                "heading": "5. Coagulation of blood",
                "html": "<p>Injury triggers clotting to prevent blood loss. A <strong>clot (coagulum)</strong> is a fibrin mesh trapping damaged cells. <strong>Thrombokinase</strong> activates <strong>prothrombin → thrombin</strong>, which converts <strong>fibrinogen → fibrin</strong> (cascade process). Platelets and tissue factors initiate the cascade. <strong>Ca²⁺</strong> is essential.</p>",
            },
            {
                "id": "bf-lymph",
                "level": 2,
                "heading": "6. Lymph (tissue fluid)",
                "html": "<p>As blood passes through capillaries, water and small solutes leave into intercellular spaces → <strong>tissue/interstitial fluid</strong> (same mineral distribution as plasma, minus most proteins). The <strong>lymphatic system</strong> collects this as <strong>lymph</strong> (colourless, with lymphocytes) and returns it to major veins. Lymph carries nutrients, hormones; <strong>lacteals</strong> in intestinal villi absorb fats.</p>",
            },
            {
                "id": "bf-circulatory-pathways",
                "level": 2,
                "heading": "7. Circulatory pathways",
                "html": "<p><strong>Fish</strong> — 2-chambered heart, single circulation (heart → gills → body → heart). <strong>Amphibians/reptiles</strong> (except crocodile) — 3-chambered, incomplete double circulation (mixed blood in single ventricle). <strong>Crocodiles, birds, mammals</strong> — 4-chambered, <strong>complete double circulation</strong> (no mixing). Closed system allows precise flow regulation.</p>",
            },
            {
                "id": "bf-human-heart",
                "level": 2,
                "heading": "8. Human heart & conduction system",
                "html": "<p>Mesodermal, fist-sized, in thoracic cavity between lungs, tilted left, in <strong>pericardium</strong>. Four chambers: right/left <strong>atria</strong> (upper), right/left <strong>ventricles</strong> (lower, thicker walls). <strong>Tricuspid</strong> (RA→RV), <strong>bicuspid/mitral</strong> (LA→LV), <strong>semilunar</strong> valves (RV→pulmonary artery, LV→aorta) ensure one-way flow. <strong>Nodal tissue</strong>: <strong>SAN</strong> (pacemaker, 70–75 impulses/min) → <strong>AVN</strong> → <strong>AV bundle (Bundle of His)</strong> → <strong>Purkinje fibres</strong>. Heart is <strong>myogenic</strong> (autoexcitable).</p>",
            },
            {
                "id": "bf-cardiac-cycle",
                "level": 2,
                "heading": "9. Cardiac cycle",
                "html": "<p>Sequential systole and diastole (~0.8 s, ~72 cycles/min). <strong>Joint diastole</strong> → SAN fires → <strong>atrial systole</strong> (~30% extra filling) → <strong>ventricular systole</strong> (AV valves close — 'lub'; semilunar open → blood to pulmonary artery/aorta) → ventricular diastole (semilunar close — 'dub'). <strong>Stroke volume</strong> ~70 mL; <strong>cardiac output</strong> = stroke volume × heart rate ≈ 5 L/min.</p>",
            },
            {
                "id": "bf-ecg",
                "level": 2,
                "heading": "10. Electrocardiogram (ECG)",
                "html": "<p>Graphical record of heart's electrical activity. <strong>P wave</strong> — atrial depolarisation; <strong>QRS complex</strong> — ventricular depolarisation/contraction onset; <strong>T wave</strong> — ventricular repolarisation. Heart rate = QRS complexes per minute. Deviations indicate abnormalities.</p>",
            },
            {
                "id": "bf-double-circulation",
                "level": 2,
                "heading": "11. Double circulation & blood vessels",
                "html": "<p><strong>Pulmonary circulation</strong>: RV → pulmonary artery → lungs (O₂ pickup) → pulmonary veins → LA. <strong>Systemic circulation</strong>: LV → aorta → tissues → vena cava → RA. Vessels have three layers: tunica intima, media, externa. <strong>Hepatic portal system</strong> — intestine → liver → systemic circulation. <strong>Coronary circulation</strong> supplies cardiac muscle.</p>",
            },
            {
                "id": "bf-regulation",
                "level": 2,
                "heading": "12. Regulation of cardiac activity",
                "html": "<p>Intrinsic (nodal tissue) plus neural/hormonal modulation. Medullary cardiac centre via <strong>ANS</strong>: <strong>sympathetic</strong> ↑rate and contractility; <strong>parasympathetic</strong> (vagus) ↓rate and conduction. <strong>Adrenal medullary hormones</strong> (adrenaline/noradrenaline) increase cardiac output.</p>",
            },
            {
                "id": "bf-disorders",
                "level": 2,
                "heading": "13. Disorders of circulatory system",
                "html": "<ul><li><strong>Hypertension</strong> — BP persistently &gt;140/90 mm Hg.</li><li><strong>CAD/atherosclerosis</strong> — arterial plaque narrows coronary vessels.</li><li><strong>Angina</strong> — chest pain from insufficient O₂ to heart muscle.</li><li><strong>Heart failure</strong> — heart cannot pump effectively (≠ cardiac arrest or heart attack).</li></ul>",
            },
        ],
    },
    {
        "id": "bio11-ch16",
        "class": 11,
        "chapterNo": 16,
        "title": "Excretory Products and Their Elimination",
        "topic": "Products and Their Elimination",
        "intro": "NCERT Class XI Chapter 16: nitrogenous waste excretion, the human excretory system, urine formation, counter-current mechanism, regulation of kidney function, and disorders.",
        "default": "ex-overview",
        "rules": [
            ("ex-disorders", r"uremia|hemodialysis|haemodialysis|dialysis|kidney transplant|renal calculi|glomerulonephritis|kidney stone|glycosuria|ketonuria|nephritis|pyelonephritis"),
            ("ex-other-organs", r"lung.*excret|liver.*excret|skin.*excret|sweat gland|sebaceous|saliva.*nitrogen|role of liver.*excret|role of lung|bile.*excret|sebum"),
            ("ex-micturition", r"micturition|urinary bladder|urethra|stretch receptor.*bladder|sphincter.*bladder|voluntary.*urin"),
            ("ex-regulation", r"\badh\b|vasopressin|antidiuretic|renin|angiotensin|aldosterone|atrial natriuretic|\banf\b|osmoreceptor|juxta.?glomerular|\bjga\b|raas|raa system"),
            ("ex-counter-current", r"counter.current|countercurrent|vasa recta|osmolar.*medull|medullary interstit|concentrated urine|1200 mosm|300 mosm|four times concentrated"),
            ("ex-tubules", r"\bpct\b|proximal convoluted|distal convoluted|\bdct\b|henle|collecting duct|loop of henle|descending limb|ascending limb|function of.*tubule|tubule.*function"),
            ("ex-urine-formation", r"glomerular filtration|\bgfr\b|reabsorption|tubular secretion|ultrafiltration|filtration slits|podocyte|urine formation|99 per cent|180 litre|125 ml"),
            ("ex-nephron", r"nephron|bowman|malpighian body|renal corpuscle|glomerulus|afferent arteriole|efferent arteriole|cortical nephron|juxtamedullary|peritubular capillar|functional unit.*kidney"),
            ("ex-human-system", r"kidney|ureter|renal pelvis|calyx|cortex.*kidney|medulla.*kidney|hilum|columns of bertini|urinary system|pyramid.*kidney"),
            ("ex-excretory-structures", r"protonephridia|flame cell|nephridia|malpighian tubule|green gland|antennal gland|ammonotel|ureotel|uricotel|excretory organ|excretory structure"),
        ],
        "sections": [
            {
                "id": "ex-overview",
                "level": 2,
                "heading": "1. Overview — excretion & nitrogenous wastes",
                "html": "<p>Metabolism produces wastes (ammonia, urea, uric acid, CO₂, ions) that must be eliminated. Major nitrogenous wastes: <strong>ammonia</strong> (most toxic, needs much water — <strong>ammonotelic</strong>: bony fishes, aquatic amphibians/insects), <strong>urea</strong> (<strong>ureotelic</strong>: mammals, terrestrial amphibians, marine fishes), <strong>uric acid</strong> (<strong>uricotelic</strong>: reptiles, birds, insects, land snails — minimal water loss).</p>",
            },
            {
                "id": "ex-excretory-structures",
                "level": 2,
                "heading": "2. Excretory structures in animals",
                "html": "<p><strong>Protonephridia/flame cells</strong> — Platyhelminthes, rotifers, Amphioxus (osmoregulation). <strong>Nephridia</strong> — annelids (earthworm). <strong>Malpighian tubules</strong> — insects. <strong>Antennal/green glands</strong> — crustaceans. <strong>Kidneys</strong> — vertebrate excretory organs.</p>",
            },
            {
                "id": "ex-human-system",
                "level": 2,
                "heading": "3. Human excretory system",
                "html": "<p>Pair of <strong>kidneys</strong> (bean-shaped, 10–12 × 5–7 × 2–3 cm, ~120–170 g), <strong>ureters</strong>, <strong>urinary bladder</strong>, <strong>urethra</strong>. Kidney: <strong>hilum</strong> (ureter, vessels, nerves), <strong>renal pelvis</strong> with calyces, outer <strong>cortex</strong>, inner <strong>medulla</strong> (pyramids), <strong>Columns of Bertini</strong>. ~1 million <strong>nephrons</strong> per kidney.</p>",
            },
            {
                "id": "ex-nephron",
                "level": 2,
                "heading": "4. Nephron structure",
                "html": "<p>Functional unit: <strong>glomerulus</strong> (afferent → efferent arteriole capillary tuft) + <strong>Bowman's capsule</strong> = <strong>Malpighian/renal corpuscle</strong>. Tubule: <strong>PCT</strong> → <strong>Henle's loop</strong> (descending + ascending) → <strong>DCT</strong> → <strong>collecting duct</strong> → renal pelvis. <strong>Cortical nephrons</strong> (short loop); <strong>juxtamedullary nephrons</strong> (long loop into medulla). <strong>Peritubular capillaries</strong> and <strong>vasa recta</strong> (U-shaped, parallel to Henle's loop) surround tubules.</p>",
            },
            {
                "id": "ex-urine-formation",
                "level": 2,
                "heading": "5. Urine formation",
                "html": "<p>Three processes: <strong>glomerular filtration</strong> (ultrafiltration through endothelium, basement membrane, podocyte slits; proteins retained; <strong>GFR</strong> ~125 mL/min ≈ 180 L/day), <strong>reabsorption</strong> (~99% of filtrate returned) and <strong>tubular secretion</strong> (H⁺, K⁺, NH₃). <strong>JGA</strong> (juxtaglomerular apparatus) regulates GFR via renin when flow/pressure falls.</p>",
            },
            {
                "id": "ex-tubules",
                "level": 2,
                "heading": "6. Function of nephron segments",
                "html": "<p><strong>PCT</strong> — brush border; reabsorbs ~70–80% water, electrolytes, all glucose/amino acids; secretes H⁺, NH₃. <strong>Henle's loop</strong> — descending limb permeable to water; ascending impermeable to water, transports electrolytes (builds medullary osmolarity). <strong>DCT</strong> — conditional Na⁺/water reabsorption; H⁺/K⁺/NH₃ secretion. <strong>Collecting duct</strong> — water reabsorption (concentrated urine), urea recycling, pH/ionic balance.</p>",
            },
            {
                "id": "ex-counter-current",
                "level": 2,
                "heading": "7. Counter-current mechanism",
                "html": "<p>Opposing flow in Henle's loop limbs and vasa recta creates a medullary osmolarity gradient (300 → ~1200 mOsmol L⁻¹) via NaCl and urea transport. Enables collecting duct to produce urine <strong>~4× concentrated</strong> over initial filtrate — vital water conservation.</p>",
            },
            {
                "id": "ex-regulation",
                "level": 2,
                "heading": "8. Regulation of kidney function",
                "html": "<p><strong>ADH/vasopressin</strong> (hypothalamus, osmoreceptors) — ↑water reabsorption in distal tubule/collecting duct. <strong>Renin-angiotensin-aldosterone</strong> (JGA) — renin → angiotensin II (vasoconstriction, ↑GFR) → aldosterone (↑Na⁺/water reabsorption). <strong>ANF</strong> (atria, ↑blood volume) — vasodilation, opposes RAAS. Together maintain blood volume, pressure and osmolarity.</p>",
            },
            {
                "id": "ex-micturition",
                "level": 2,
                "heading": "9. Micturition",
                "html": "<p>Urine stored in bladder until ~200–300 mL stretches walls → stretch receptors → CNS → motor signals → bladder smooth muscle contracts, urethral sphincter relaxes → <strong>micturition</strong> (<strong>micturition reflex</strong>; voluntary override in adults). Normal output ~1–1.5 L/day; urine slightly acidic (pH ~6), ~25–30 g urea/day.</p>",
            },
            {
                "id": "ex-other-organs",
                "level": 2,
                "heading": "10. Role of other organs in excretion",
                "html": "<p><strong>Lungs</strong> — CO₂ (~200 mL/min) and water vapour. <strong>Liver</strong> — bile pigments (bilirubin, biliverdin), cholesterol, steroids, drugs. <strong>Skin</strong> — sweat (NaCl, urea, lactic acid); sebaceous glands (sebum: sterols, waxes). Small nitrogenous wastes in saliva.</p>",
            },
            {
                "id": "ex-disorders",
                "level": 2,
                "heading": "11. Disorders of excretory system",
                "html": "<ul><li><strong>Uraemia</strong> — urea accumulation; treated by <strong>haemodialysis</strong> (artificial kidney) or <strong>kidney transplant</strong>.</li><li><strong>Renal calculi</strong> — kidney stones (oxalates, etc.).</li><li><strong>Glomerulonephritis</strong> — glomerular inflammation.</li><li><strong>Glycosuria/ketonuria</strong> — diagnostic of diabetes mellitus.</li></ul>",
            },
        ],
    },
    {
        "id": "bio11-ch17",
        "class": 11,
        "chapterNo": 17,
        "title": "Locomotion and Movement",
        "topic": "Locomotion and Movement",
        "intro": "NCERT Class XI Chapter 17: types of movement, muscle structure and contraction, the skeletal system, joints, and disorders of the muscular and skeletal systems.",
        "default": "lm-overview",
        "rules": [
            ("lm-disorders", r"myasthenia|muscular dystrophy|tetany|arthritis|osteoporosis|gout|paralysis.*muscle"),
            ("lm-joints", r"\bjoint\b|synovial|fibrous joint|cartilaginous joint|ball and socket|hinge joint|pivot joint|gliding joint|saddle joint|fulcrum|articulat"),
            ("lm-appendicular", r"pectoral girdle|pelvic girdle|scapula|clavicle|coxal|ilium|ischium|pubis|acetabulum|humerus|femur|radius|ulna|tibia|fibula|carpal|tarsal|metacarpal|metatarsal|phalang|patella|glenoid|appendicular"),
            ("lm-axial-skeleton", r"skull|vertebra|vertebral column|sternum|hyoid|atlas|axis|cervical|thoracic|lumbar|sacral|coccygeal|occipital|cranial|floating rib|true rib|false rib|ear ossicle|malleus|incus|stapes|rib cage|dicondylic|bicephalic"),
            ("lm-skeletal-system", r"skeletal system|206 bone|axial skeleton|cartilage|chondroitin|bone matrix|calcium.*bone|connective tissue.*bone"),
            ("lm-contraction", r"sliding filament|cross bridge|neuromuscular|motor end plate|acetylcholine.*muscle|sarcoplasmic reticulum.*ca|muscle contraction|contraction.*muscle|relaxation.*muscle|fatigue.*muscle|red fibre|white fibre|myoglobin|motor unit|action potential.*sarcolemma"),
            ("lm-contractile-proteins", r"actin|myosin|troponin|tropomyosin|meromyosin|thin filament|thick filament|i.band|a.band|z.line|h.zone|m.line|f.actin|g.actin"),
            ("lm-muscle-structure", r"sarcomere|muscle fibre|fascicle|sarcolemma|sarcoplasm|myofibril|myofilament|striat.*muscle|syncitium|syncytium"),
            ("lm-muscle-types", r"skeletal muscle|smooth muscle|cardiac muscle|voluntary muscle|involuntary muscle|visceral muscle|striated.*voluntary|non.striated"),
            ("lm-overview", r"locomotion|amoeboid|ciliary movement|pseudopodia|types of movement|flagellar movement"),
        ],
        "sections": [
            {
                "id": "lm-overview",
                "level": 2,
                "heading": "1. Movement & locomotion",
                "html": "<p>Living organisms show diverse movements. Human cells exhibit <strong>amoeboid</strong> (macrophages, leucocytes), <strong>ciliary</strong> (trachea, oviduct) and <strong>muscular</strong> movements. <strong>Locomotion</strong> is voluntary movement changing body position (walking, running, swimming). All locomotion involves movement but not vice versa. Locomotion aids food, shelter, mate and escape.</p>",
            },
            {
                "id": "lm-muscle-types",
                "level": 2,
                "heading": "2. Types of muscles",
                "html": "<p>Muscle (~40–50% body weight) — mesodermal, excitable, contractile, extensible, elastic. <strong>Skeletal (striated, voluntary)</strong> — attached to skeleton, striped, multinucleate. <strong>Smooth (visceral, non-striated, involuntary)</strong> — hollow organs (GI tract, vessels), spindle-shaped, uninucleate. <strong>Cardiac</strong> — heart only, striated, branched, involuntary, intercalated discs.</p>",
            },
            {
                "id": "lm-muscle-structure",
                "level": 2,
                "heading": "3. Skeletal muscle structure",
                "html": "<p>Muscle → <strong>fascicles</strong> (bundles) → <strong>muscle fibres</strong> (syncytium: sarcolemma, multinucleate sarcoplasm, rich <strong>sarcoplasmic reticulum</strong> storing Ca²⁺). Each fibre has parallel <strong>myofibrils</strong> with alternating dark <strong>A bands</strong> (myosin) and light <strong>I bands</strong> (actin). <strong>Z line</strong> bisects each I band. <strong>Sarcomere</strong> = region between two Z lines (functional contractile unit). <strong>H zone</strong> = central thick-filament only region.</p>",
            },
            {
                "id": "lm-contractile-proteins",
                "level": 2,
                "heading": "4. Contractile proteins",
                "html": "<p><strong>Actin (thin)</strong> — F-actin (polymer of G-actin) + tropomyosin + troponin (troponin masks myosin-binding sites at rest). <strong>Myosin (thick)</strong> — polymer of <strong>meromyosins</strong> (HMM head with ATPase + actin-binding sites; LMM tail). Cross-bridges form between myosin heads and actin during contraction.</p>",
            },
            {
                "id": "lm-contraction",
                "level": 2,
                "heading": "5. Mechanism of muscle contraction",
                "html": "<p><strong>Sliding filament theory</strong>: CNS → motor neuron → <strong>neuromuscular junction</strong> (ACh release) → action potential in sarcolemma → Ca²⁺ from SR → Ca²⁺ binds troponin → actin sites exposed → myosin cross-bridges (ATP hydrolysis) pull actin → sarcomere shortens (I band and H zone shrink; A band unchanged). Ca²⁺ pumped back → relaxation. Repeated stimulation → lactic acid → <strong>fatigue</strong>. <strong>Red fibres</strong> (myoglobin-rich, aerobic); <strong>white fibres</strong> (less myoglobin, anaerobic).</p>",
            },
            {
                "id": "lm-skeletal-system",
                "level": 2,
                "heading": "6. Skeletal system overview",
                "html": "<p><strong>206 bones</strong> and cartilages — specialised connective tissue (bone: hard Ca²⁺ matrix; cartilage: pliable chondroitin matrix). Two divisions: <strong>axial</strong> (80 bones) and <strong>appendicular</strong>. Supports movement, protects organs, provides muscle attachment.</p>",
            },
            {
                "id": "lm-axial-skeleton",
                "level": 2,
                "heading": "7. Axial skeleton",
                "html": "<p><strong>Skull</strong> (22 bones: 8 cranial + 14 facial), <strong>hyoid</strong>, 3 <strong>ear ossicles</strong>/ear (malleus, incus, stapes), <strong>vertebral column</strong> (26 vertebrae: 7 cervical, 12 thoracic, 5 lumbar, 1 sacral fused, 1 coccygeal fused; atlas articulates with occipital condyles — <strong>dicondylic skull</strong>), <strong>sternum</strong>, <strong>12 pairs of ribs</strong> (7 true, 3 false/vertebrochondral, 2 floating) forming <strong>rib cage</strong>.</p>",
            },
            {
                "id": "lm-appendicular",
                "level": 2,
                "heading": "8. Appendicular skeleton & girdles",
                "html": "<p>Each limb = 30 bones. <strong>Forelimb</strong>: humerus, radius, ulna, 8 carpals, 5 metacarpals, 14 phalanges. <strong>Hindlimb</strong>: femur (longest bone), tibia, fibula, patella, 7 tarsals, 5 metatarsals, 14 phalanges. <strong>Pectoral girdle</strong> — scapula + clavicle (glenoid cavity with humerus). <strong>Pelvic girdle</strong> — two coxal bones (ilium, ischium, pubis fused; acetabulum with femur); pubic symphysis ventrally.</p>",
            },
            {
                "id": "lm-joints",
                "level": 2,
                "heading": "9. Joints",
                "html": "<p>Points of contact between bones/cartilage; muscles act through joints as levers. <strong>Fibrous</strong> — immovable (skull sutures). <strong>Cartilaginous</strong> — limited movement (intervertebral discs). <strong>Synovial</strong> — fluid-filled cavity, freely movable: ball-and-socket (shoulder), hinge (knee, elbow), pivot (atlas-axis), gliding (carpals), saddle (thumb carpometacarpal).</p>",
            },
            {
                "id": "lm-disorders",
                "level": 2,
                "heading": "10. Disorders of muscular & skeletal system",
                "html": "<ul><li><strong>Myasthenia gravis</strong> — autoimmune neuromuscular junction disorder.</li><li><strong>Muscular dystrophy</strong> — progressive skeletal muscle degeneration.</li><li><strong>Tetany</strong> — rapid spasms from low Ca²⁺.</li><li><strong>Arthritis</strong> — joint inflammation.</li><li><strong>Osteoporosis</strong> — age-related bone mass loss (↓estrogen).</li><li><strong>Gout</strong> — uric acid crystals in joints.</li></ul>",
            },
        ],
    },
]


def main() -> int:
    notes = json.loads((ROOT / "notes.json").read_text(encoding="utf-8"))
    note_links = json.loads((ROOT / "note_links.json").read_text(encoding="utf-8"))

    for ch in CHAPTERS:
        rules = ch["rules"]
        default = ch["default"]
        chapter_note = {
            "id": ch["id"],
            "class": ch["class"],
            "chapterNo": ch["chapterNo"],
            "title": ch["title"],
            "topic": ch["topic"],
            "intro": ch["intro"],
            "sections": ch["sections"],
        }
        upsert_chapter_notes(notes, chapter_note)

        questions = load_bank(ch["topic"])
        links = build_links(questions, rules, default)
        upsert_chapter_links(note_links, ch["id"], ch["topic"], links)

        print(f"\n{ch['id']} — {len(ch['sections'])} sections, {len(links)} links (bank={len(questions)})")
        print_distribution(links)

    (ROOT / "notes.json").write_text(
        json.dumps(notes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    (ROOT / "note_links.json").write_text(
        json.dumps(note_links, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    errs = verify_all()
    if errs:
        print("\nVERIFICATION FAILED:")
        for e in errs:
            print(e)
        return 1

    print("\nAll linked chapters pass verification (0 missing, 0 orphan).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
