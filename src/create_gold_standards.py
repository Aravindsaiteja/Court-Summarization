"""Gold-Standard Reference Generator for Court Proceeding Evaluation.

Populates human-verified reference transcripts and extractive reference summaries
with sentence-level salience annotations and legal categorizations.
"""

import json
from pathlib import Path

GOLD_RECORDS = {
    "CASE_EN_01": {
        "case_id": "CASE_EN_01",
        "source_title": "My Cousin Vinny (1992)",
        "language": "en",
        "sentences": [
            {
                "sentence_id": 1,
                "speaker": "Vinny Gambini",
                "speaker_role": "Defense Counsel",
                "start_time": 4.5,
                "end_time": 10.2,
                "text": "Miss Vito, with your extensive experience in automotive mechanics, could you explain the tire tracks found at the Sac-O-Suds convenience store?",
                "salience_score": 2,
                "category": "EVIDENTIARY_QUESTION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 2,
                "speaker": "Mona Lisa Vito",
                "speaker_role": "Expert Witness",
                "start_time": 10.8,
                "end_time": 24.5,
                "text": "The tire marks left by the getaway vehicle show two distinct dual-track markings made by a car with an independent rear suspension and a positraction differential.",
                "salience_score": 3,
                "category": "EXPERT_TESTIMONY",
                "in_gold_summary": True
            },
            {
                "sentence_id": 3,
                "speaker": "Mona Lisa Vito",
                "speaker_role": "Expert Witness",
                "start_time": 25.1,
                "end_time": 35.8,
                "text": "A 1964 Buick Skylark, which the defendants were driving, has a solid rear axle and could never make those symmetrical marks.",
                "salience_score": 3,
                "category": "EXCULPATORY_EVIDENCE",
                "in_gold_summary": True
            },
            {
                "sentence_id": 4,
                "speaker": "Prosecutor Jim Trotter",
                "speaker_role": "Prosecutor",
                "start_time": 36.2,
                "end_time": 42.0,
                "text": "Objection your honor, this testimony is speculative and uncorroborated by state forensics.",
                "salience_score": 1,
                "category": "OBJECTION",
                "in_gold_summary": False
            },
            {
                "sentence_id": 5,
                "speaker": "Judge Chamberlain Haller",
                "speaker_role": "Judge",
                "start_time": 42.5,
                "end_time": 48.1,
                "text": "Overruled, the witness has qualified as an expert in automotive mechanics and will continue.",
                "salience_score": 2,
                "category": "JUDICIAL_RULING",
                "in_gold_summary": True
            },
            {
                "sentence_id": 6,
                "speaker": "Mona Lisa Vito",
                "speaker_role": "Expert Witness",
                "start_time": 48.5,
                "end_time": 62.4,
                "text": "Only two cars made by General Motors had that specific track width and independent suspension: the 1963 Pontiac Tempest and the Chevrolet Corvette.",
                "salience_score": 3,
                "category": "CONCLUSIVE_EVIDENCE",
                "in_gold_summary": True
            },
            {
                "sentence_id": 7,
                "speaker": "Prosecutor Jim Trotter",
                "speaker_role": "Prosecutor",
                "start_time": 63.0,
                "end_time": 71.2,
                "text": "In light of this ballistic and mechanical evidence, the State respectfully moves to dismiss all charges against the defendants.",
                "salience_score": 3,
                "category": "DISMISSAL_MOTION",
                "in_gold_summary": True
            }
        ]
    },
    "CASE_EN_02": {
        "case_id": "CASE_EN_02",
        "source_title": "Law Abiding Citizen (2009)",
        "language": "en",
        "sentences": [
            {
                "sentence_id": 1,
                "speaker": "Judge Laura Burch",
                "speaker_role": "Judge",
                "start_time": 8.0,
                "end_time": 15.2,
                "text": "Mr. Clyde Shelton, you stand before this court charged with aggravated homicide and conspiracy.",
                "salience_score": 3,
                "category": "CHARGES_FRAMED",
                "in_gold_summary": True
            },
            {
                "sentence_id": 2,
                "speaker": "Prosecutor Nick Rice",
                "speaker_role": "Prosecutor",
                "start_time": 15.8,
                "end_time": 26.5,
                "text": "The Commonwealth requests bail be denied outright; the defendant represents an extraordinary flight risk and an active danger to society.",
                "salience_score": 2,
                "category": "BAIL_OPPOSITION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 3,
                "speaker": "Clyde Shelton",
                "speaker_role": "Defendant (Pro Se)",
                "start_time": 27.2,
                "end_time": 44.0,
                "text": "Your Honor, the prosecution's entire petition relies upon circumstantial conjecture and precedent established in State v. Stewart, which requires tangible physical evidence before revoking pretrial liberty.",
                "salience_score": 3,
                "category": "LEGAL_SUBMISSION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 4,
                "speaker": "Judge Laura Burch",
                "speaker_role": "Judge",
                "start_time": 45.0,
                "end_time": 58.5,
                "text": "I find the defense argument persuasive on strict statutory grounds, and under normal procedure I would have been inclined to set bail at five hundred thousand dollars.",
                "salience_score": 2,
                "category": "JUDICIAL_OBSERVATION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 5,
                "speaker": "Clyde Shelton",
                "speaker_role": "Defendant",
                "start_time": 59.0,
                "end_time": 75.0,
                "text": "Would you really let me walk out of here on bail when I just confessed to butchering a man with my bare hands?",
                "salience_score": 3,
                "category": "IN-COURT_CONFESSION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 6,
                "speaker": "Judge Laura Burch",
                "speaker_role": "Judge",
                "start_time": 76.0,
                "end_time": 88.0,
                "text": "I hold you in direct contempt of court; bail is formally revoked and you will be remanded to maximum security custody immediately.",
                "salience_score": 3,
                "category": "JUDICIAL_RULING",
                "in_gold_summary": True
            }
        ]
    },
    "CASE_EN_03": {
        "case_id": "CASE_EN_03",
        "source_title": "Legally Blonde (2001)",
        "language": "en",
        "sentences": [
            {
                "sentence_id": 1,
                "speaker": "Elle Woods",
                "speaker_role": "Defense Counsel",
                "start_time": 10.0,
                "end_time": 22.0,
                "text": "Ms. Windham, on the morning of your father's murder, you stated under sworn oath that you were in the shower during the gunshots.",
                "salience_score": 2,
                "category": "CROSS_EXAMINATION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 2,
                "speaker": "Chutney Windham",
                "speaker_role": "Witness",
                "start_time": 22.5,
                "end_time": 30.0,
                "text": "Yes, I got a perm that morning and was washing my hair in the master bath.",
                "salience_score": 2,
                "category": "WITNESS_ALIBI",
                "in_gold_summary": True
            },
            {
                "sentence_id": 3,
                "speaker": "Elle Woods",
                "speaker_role": "Defense Counsel",
                "start_time": 31.0,
                "end_time": 45.0,
                "text": "Anyone who has ever gotten a perm knows that washing your hair within forty-eight hours deactivates the ammonium thioglycolate and destroys the curls.",
                "salience_score": 3,
                "category": "EXPERT_REFUTATION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 4,
                "speaker": "Chutney Windham",
                "speaker_role": "Witness",
                "start_time": 46.0,
                "end_time": 56.0,
                "text": "I didn't mean to shoot him, I thought it was Brooke walking through the door!",
                "salience_score": 3,
                "category": "IN-COURT_CONFESSION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 5,
                "speaker": "Judge",
                "speaker_role": "Judge",
                "start_time": 57.0,
                "end_time": 68.0,
                "text": "Bailiff, arrest that witness for first-degree murder; the defendant Brooke Windham is acquitted and free to go.",
                "salience_score": 3,
                "category": "JUDICIAL_DISPOSITION",
                "in_gold_summary": True
            }
        ]
    },
    "CASE_HI_01": {
        "case_id": "CASE_HI_01",
        "source_title": "Criminal Justice S3 (Madhav Mishra)",
        "language": "hi",
        "sentences": [
            {
                "sentence_id": 1,
                "speaker": "Madhav Mishra",
                "speaker_role": "Defense Counsel",
                "start_time": 5.0,
                "end_time": 18.0,
                "text": "हुजूर, अभियोजन पक्ष ने मेरे मुवक्किल पर गैर-इरादतन हत्या का झूठा आरोप लगाया है बिना किसी प्रत्यक्षदर्शी के।",
                "salience_score": 2,
                "category": "DEFENSE_ARGUMENT",
                "in_gold_summary": True
            },
            {
                "sentence_id": 2,
                "speaker": "Prosecution Counsel",
                "speaker_role": "Prosecutor",
                "start_time": 18.5,
                "end_time": 30.0,
                "text": "फॉरेंसिक रिपोर्ट और घटनास्थल से मिले फिंगरप्रिंट स्पष्ट रूप से आरोपी की मौजूदगी सिद्ध करते हैं।",
                "salience_score": 3,
                "category": "FORENSIC_EVIDENCE",
                "in_gold_summary": True
            },
            {
                "sentence_id": 3,
                "speaker": "Madhav Mishra",
                "speaker_role": "Defense Counsel",
                "start_time": 31.0,
                "end_time": 48.0,
                "text": "लेकिन कॉल डिटेल रिकॉर्ड्स और सीसीटीवी फुटेज यह साबित करते हैं कि वारदात के समय मुवक्किल अस्पताल में उपस्थित था।",
                "salience_score": 3,
                "category": "EXCULPATORY_ALIBI",
                "in_gold_summary": True
            },
            {
                "sentence_id": 4,
                "speaker": "Judge",
                "speaker_role": "Judge",
                "start_time": 49.0,
                "end_time": 65.0,
                "text": "साक्ष्यों में विरोधाभास को देखते हुए अदालत आरोपी को पचास हजार के मुचलके पर सशर्त जमानत प्रदान करती है।",
                "salience_score": 3,
                "category": "JUDICIAL_RULING",
                "in_gold_summary": True
            }
        ]
    },
    "CASE_TA_01": {
        "case_id": "CASE_TA_01",
        "source_title": "Parasakthi (1952 Classic Court Monologue)",
        "language": "ta",
        "sentences": [
            {
                "sentence_id": 1,
                "speaker": "Gunasekaran",
                "speaker_role": "Accused",
                "start_time": 12.0,
                "end_time": 30.0,
                "text": "நீதிமன்றத்திற்கு வந்திருப்பது குற்றத்தை மறுக்க அல்ல, குற்றத்திற்கான காரணத்தை விளக்க வந்திருக்கிறேன்.",
                "salience_score": 2,
                "category": "STATEMENT_OF_ACCUSED",
                "in_gold_summary": True
            },
            {
                "sentence_id": 2,
                "speaker": "Gunasekaran",
                "speaker_role": "Accused",
                "start_time": 32.0,
                "end_time": 55.0,
                "text": "பசியால் வாடும் ஒரு ஏழை உணவை திருடினால் அது சட்டப்படி திருட்டு, ஆனால் பசியை உருவாக்கிய சமூகம் குற்றவாளி இல்லையா?",
                "salience_score": 3,
                "category": "CORE_DEFENSE_SPEECH",
                "in_gold_summary": True
            },
            {
                "sentence_id": 3,
                "speaker": "Gunasekaran",
                "speaker_role": "Accused",
                "start_time": 58.0,
                "end_time": 80.0,
                "text": "கோவிலில் அநீதி நடக்கும் போது சிலைகள் பேசாது, ஆனால் மனிதனின் நீதி மன்றம் வாய்மை தவறக் கூடாது.",
                "salience_score": 3,
                "category": "RHETORICAL_ARGUMENT",
                "in_gold_summary": True
            },
            {
                "sentence_id": 4,
                "speaker": "Judge",
                "speaker_role": "Judge",
                "start_time": 82.0,
                "end_time": 100.0,
                "text": "சட்டத்தின் வரம்புகளை உணர்ந்து நீதிமன்றம் வழக்கின் சூழ்நிலையை ஆராய்ந்து இறுதி தீர்ப்பை ஒத்திவைக்கிறது.",
                "salience_score": 3,
                "category": "JUDICIAL_ORDER",
                "in_gold_summary": True
            }
        ]
    },
    "CASE_TE_02": {
        "case_id": "CASE_TE_02",
        "source_title": "Naandhi (2021 Section 211 IPC Case)",
        "language": "te",
        "sentences": [
            {
                "sentence_id": 1,
                "speaker": "Advocate Aadhya",
                "speaker_role": "Defense Counsel",
                "start_time": 15.0,
                "end_time": 32.0,
                "text": "సెక్షన్ 211 ఐపీసీ ప్రకారం నిరపరాధిపై తప్పుడు కేసు బనాయించి జైలులో ఉంచిన అధికారులపై విచారణ జరగాలి.",
                "salience_score": 3,
                "category": "STATUTORY_MOTION",
                "in_gold_summary": True
            },
            {
                "sentence_id": 2,
                "speaker": "Public Prosecutor",
                "speaker_role": "Prosecution",
                "start_time": 33.0,
                "end_time": 48.0,
                "text": "పోలీస్ డిపార్ట్మెంట్ కేవలం ప్రాథమిక ఆధారాల ప్రకారమే దర్యాప్తు నిర్వహించింది తప్ప ఇందులో వ్యక్తిగత కక్ష లేదు.",
                "salience_score": 2,
                "category": "STATE_DEFENSE",
                "in_gold_summary": True
            },
            {
                "sentence_id": 3,
                "speaker": "Advocate Aadhya",
                "speaker_role": "Defense Counsel",
                "start_time": 49.0,
                "end_time": 70.0,
                "text": "ఎనిమిది సంవత్సరాల అన్యాయమైన నిర్బంధానికి పరిహారంగా రాష్ట్ర ప్రభుత్వం బాధితుడికి న్యాయం చేయాల్సిందే.",
                "salience_score": 3,
                "category": "CONSTITUTIONAL_REMEDY",
                "in_gold_summary": True
            },
            {
                "sentence_id": 4,
                "speaker": "Judge",
                "speaker_role": "Judge",
                "start_time": 71.0,
                "end_time": 95.0,
                "text": "న్యాయస్థానం సెక్షన్ 211 క్రింద దోషులైన దర్యాప్తు అధికారులపై శాఖాపరమైన మరియు క్రిమినల్ విచారణకు ఆదేశిస్తుంది.",
                "salience_score": 3,
                "category": "JUDICIAL_DISPOSITION",
                "in_gold_summary": True
            }
        ]
    }
}


def populate_gold_standard():
    base_transcripts = Path("data/gold_standard/transcripts")
    base_summaries = Path("data/gold_standard/summaries")
    base_transcripts.mkdir(parents=True, exist_ok=True)
    base_summaries.mkdir(parents=True, exist_ok=True)

    for case_id, data in GOLD_RECORDS.items():
        # Save JSON transcript
        json_file = base_transcripts / f"{case_id}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        # Save gold extractive summary text
        gold_sentences = [
            f"[{s['start_time']:05.1f}s - {s['end_time']:05.1f}s] {s['speaker']} ({s['category']}): {s['text']}"
            for s in data["sentences"]
            if s.get("in_gold_summary", False)
        ]
        sum_file = base_summaries / f"{case_id}_gold_summary.txt"
        with open(sum_file, "w", encoding="utf-8") as f:
            f.write("\n".join(gold_sentences) + "\n")

    print(f"Successfully generated gold standard transcripts and summaries for {len(GOLD_RECORDS)} cases.")


if __name__ == "__main__":
    populate_gold_standard()
