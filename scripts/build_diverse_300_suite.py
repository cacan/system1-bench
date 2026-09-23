"""
Build the 300-case diverse benchmark suite for System1-Bench.
Combines 5 diverse domains (60 cases each = 300 cases total):
1. Banking77 (PolyAI) - Fintech & banking service triage
2. CLINC150 (clinc_oos) - Conversational multi-domain assistant & out-of-scope detection
3. Trust & Safety (CivilComments / Toxicity) - Content moderation & policy enforcement
4. E-Commerce Support - Retail orders, logistics, returns, and dispute triage
5. Business & Tech News (AG News) - Media, financial, and topic categorization
"""

import json
import urllib.request
import csv
import io
import random
from pathlib import Path

random.seed(42)

def build_banking77_cases(count=60):
    url = "https://raw.githubusercontent.com/PolyAI-LDN/task-specific-datasets/master/banking_data/test.csv"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req).read().decode("utf-8")
    reader = csv.DictReader(io.StringIO(data))
    all_rows = list(reader)

    # Department mapping for Banking77 intents
    dept_map = {
        "security_fraud": [
            "compromised_card", "card_swallowed", "card_payment_not_recognised", 
            "cash_withdrawal_not_recognised", "direct_debit_payment_not_recognised", 
            "lost_or_stolen_card", "lost_or_stolen_phone"
        ],
        "transfers_payments": [
            "failed_transfer", "pending_transfer", "declined_transfer", 
            "declined_card_payment", "declined_cash_withdrawal", "cancel_transfer", 
            "balance_not_updated_after_bank_transfer", "transfer_into_account",
            "transfer_timing", "transfer_fee_charged", "beneficiary_not_allowed"
        ],
        "account_access": [
            "change_pin", "pin_blocked", "edit_personal_details", "verify_identity", 
            "verify_my_identity", "passcode_forgotten", "age_limit", "country_support"
        ],
        "card_logistics": [
            "card_arrival", "card_delivery_estimate", "get_physical_card", 
            "get_disposable_virtual_card", "getting_spare_card", "card_linking", 
            "card_not_working", "contactless_not_working", "activate_my_card"
        ],
        "billing_fees": [
            "card_payment_fee_charged", "cash_withdrawal_charge", "exchange_charge", 
            "extra_charge_on_statement", "exchange_rate", "card_payment_wrong_exchange_rate", 
            "top_up_reverted"
        ]
    }

    # Reverse lookup intent -> department
    intent_to_dept = {}
    for dept, intents in dept_map.items():
        for intent in intents:
            intent_to_dept[intent] = dept

    questions_def = {
        "department": {
            "type": "choice",
            "instructions": "Which banking department should handle this customer inquiry?",
            "criteria": {
                "security_fraud": "Unauthorized charges, compromised or stolen cards, and fraud alerts.",
                "transfers_payments": "Bank transfers, deposits, payment failures, or currency transfers.",
                "account_access": "Login credentials, PIN reset, identity verification, and personal profile.",
                "card_logistics": "New card issuance, tracking delivery, card activation, or card defects.",
                "billing_fees": "Fee inquiries, exchange rates, statement charges, or pricing questions."
            }
        },
        "urgent_fraud": {
            "type": "noul",
            "instructions": "Does this report indicate an urgent security or fraud emergency?"
        },
        "severity": {
            "type": "score",
            "instructions": "How severe is the disruption to the customer?",
            "criteria": [
                "Informational inquiry; no disruption.",
                "Routine service request; minor inconvenience.",
                "Significant friction; delayed payment or declined transaction.",
                "Critical emergency; unauthorized funds drain or compromised security."
            ]
        }
    }

    selected = []
    # Collect balanced samples across departments
    by_dept = {d: [] for d in dept_map}
    for row in all_rows:
        cat = row["category"]
        dept = intent_to_dept.get(cat)
        if dept:
            by_dept[dept].append(row)

    cases_per_dept = count // len(dept_map) # 12 per dept
    for dept, rows in by_dept.items():
        random.shuffle(rows)
        for r in rows[:cases_per_dept]:
            cat = r["category"]
            text = r["text"]
            is_fraud = dept == "security_fraud"
            if is_fraud:
                severity = 3
            elif dept in ("transfers_payments", "billing_fees"):
                severity = 2 if "declined" in cat or "failed" in cat or "extra_charge" in cat else 1
            elif dept == "card_logistics":
                severity = 2 if "not_working" in cat else 1
            else:
                severity = 1 if "blocked" in cat else 0

            selected.append({
                "id": f"bank-{len(selected)+1:03d}",
                "domain": "banking",
                "state": text,
                "questions": questions_def,
                "labels": {
                    "department": dept,
                    "urgent_fraud": is_fraud,
                    "severity": severity
                }
            })

    return selected[:count]


def build_clinc_cases(count=60):
    url = "https://raw.githubusercontent.com/clinc/oos-eval/master/data/data_small.json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = json.loads(urllib.request.urlopen(req).read().decode("utf-8"))
    
    # 5 domain categories
    # clinc has intents across domains, plus oos
    travel_intents = {"flight_status", "book_flight", "flight_delay", "travel_alert", "timezone", "rental_car", "hotel_reservation"}
    work_intents = {"schedule_meeting", "meeting_schedule", "pto_request", "calendar_update", "payday", "todo_list"}
    home_auto_intents = {"cook_time", "recipe", "shopping_list", "oil_change_how", "tire_pressure", "traffic", "gas"}
    utility_intents = {"weather", "calculator", "alarm", "timer", "definition", "spelling", "translate"}
    
    questions_def = {
        "domain": {
            "type": "choice",
            "instructions": "Which domain does this assistant query belong to?",
            "criteria": {
                "travel": "Flights, hotel bookings, travel times, and destinations.",
                "work": "Meetings, calendars, payroll, PTO, and office tasks.",
                "home_auto": "Cooking, household items, grocery lists, car maintenance, and traffic.",
                "utility": "Weather, alarms, timers, translation, and general utilities.",
                "oos": "Out-of-scope or unsupported requests outside assistant capabilities."
            }
        },
        "oos_fallback": {
            "type": "noul",
            "instructions": "Is this query out of scope, requiring an assistant fallback response?"
        },
        "complexity": {
            "type": "score",
            "instructions": "How complex is the requested action?",
            "criteria": [
                "Simple informational query (e.g. check time, weather).",
                "Single-step lookup or reminder setting.",
                "Multi-parameter transactional action (booking, reservation, transfer).",
                "Complex out-of-scope or ambiguous intent requiring human resolution."
            ]
        }
    }

    cases = []
    # Collect from test and oos_test
    test_rows = data.get("test", [])
    oos_rows = data.get("oos_test", [])

    categorized = {"travel": [], "work": [], "home_auto": [], "utility": [], "oos": []}
    for text, intent in test_rows:
        if intent in travel_intents:
            categorized["travel"].append(text)
        elif intent in work_intents:
            categorized["work"].append(text)
        elif intent in home_auto_intents:
            categorized["home_auto"].append(text)
        elif intent in utility_intents:
            categorized["utility"].append(text)
    
    for item in oos_rows:
        text = item[0] if isinstance(item, list) else item
        categorized["oos"].append(text)

    per_cat = count // 5 # 12 each
    for dom, texts in categorized.items():
        random.shuffle(texts)
        for t in texts[:per_cat]:
            is_oos = (dom == "oos")
            if is_oos:
                complexity = 3
            elif dom == "travel":
                complexity = 2
            elif dom == "work":
                complexity = 1
            elif dom == "home_auto":
                complexity = 1
            else:
                complexity = 0

            cases.append({
                "id": f"assistant-{len(cases)+1:03d}",
                "domain": "conversational_assistant",
                "state": t,
                "questions": questions_def,
                "labels": {
                    "domain": dom,
                    "oos_fallback": is_oos,
                    "complexity": complexity
                }
            })

    return cases[:count]


def build_moderation_cases(count=60):
    questions_def = {
        "violation_type": {
            "type": "choice",
            "instructions": "What community guideline category does this comment fall under?",
            "criteria": {
                "clean": "Constructive, civil, respectful discussion without policy violations.",
                "harassment": "Targeted hostility, bullying, insults, or personal mocking.",
                "hate_speech": "Dehumanizing, hateful, or discriminatory attacks on protected groups.",
                "profanity": "Excessive crude, vulgar, or obscene language without direct harassment."
            }
        },
        "policy_violation": {
            "type": "noul",
            "instructions": "Does this content violate community safety policies and require intervention?"
        },
        "enforcement_action": {
            "type": "score",
            "instructions": "What moderation action level should be enforced?",
            "criteria": [
                "Approve: No action required; safe for publication.",
                "Low severity: Allow with warning or mild filter.",
                "Medium severity: Hide comment and flag account for human review.",
                "High severity: Immediate removal and temporary/permanent suspension."
            ]
        }
    }

    # 60 carefully curated realistic moderation comments (clean, harassment, hate_speech, profanity)
    # Balanced 15 of each category
    samples = [
        # CLEAN (15)
        ("I strongly disagree with the policy, but here are three data points why it won't work in practice.", "clean", False, 0),
        ("Thank you for sharing your perspective, this really helped me understand the topic better.", "clean", False, 0),
        ("Could you clarify what source was used for the second economic chart?", "clean", False, 0),
        ("Great breakdown of the technical tradeoffs between PostgreSQL and SQLite.", "clean", False, 0),
        ("I found the first chapter fascinating, especially the historical analysis of trade routes.", "clean", False, 0),
        ("While the initial rollout had some minor glitches, the new update resolved my sync issues completely.", "clean", False, 0),
        ("Can anyone recommend good introductory tutorials for PyTorch 2.0 distributed training?", "clean", False, 0),
        ("The conference schedule looks packed this year. Looking forward to the keynote on Wednesday.", "clean", False, 0),
        ("Please remember to submit your pull requests by 5 PM so we can complete the sprint review.", "clean", False, 0),
        ("I appreciate your patience while we investigated this edge case in the tokenizer.", "clean", False, 0),
        ("The author presents a balanced overview of renewable energy storage technologies.", "clean", False, 0),
        ("Our team benchmarked both solutions and observed virtually identical memory footprints.", "clean", False, 0),
        ("Has anyone tested this on Windows 11 with WSL2 enabled?", "clean", False, 0),
        ("Congratulations to the research team on publishing this open-access dataset.", "clean", False, 0),
        ("An insightful writeup. The section explaining attention sinks was particularly clear.", "clean", False, 0),

        # HARASSMENT (15)
        ("You are completely brainless. Stop commenting before you embarrass yourself even more.", "harassment", True, 2),
        ("Nobody cares about your worthless opinion. Get off this forum and never come back.", "harassment", True, 2),
        ("You must be an absolute idiot if you think this design makes any sense at all.", "harassment", True, 2),
        ("Everyone in this thread is laughing at how incompetent you are.", "harassment", True, 2),
        ("Go cry to your mommy, pathetic loser. You have no business writing code.", "harassment", True, 3),
        ("You're a disgrace to the entire industry. Do us all a favor and resign immediately.", "harassment", True, 2),
        ("Shut up already, your comments make everyone nauseous.", "harassment", True, 2),
        ("You are so profoundly stupid that it actually hurts to read your replies.", "harassment", True, 2),
        ("Look at this clown pretending to understand statistics. Absolute joke of a human.", "harassment", True, 2),
        ("We are going to find you and make sure you pay for what you said online.", "harassment", True, 3),
        ("Keep talking like that and see what happens to you in real life.", "harassment", True, 3),
        ("You are a dishonest, manipulative creep and everyone knows it.", "harassment", True, 2),
        ("I hope your career is completely ruined, you utter fraud.", "harassment", True, 2),
        ("Don't ever show your face here again or you'll regret it deeply.", "harassment", True, 3),
        ("You are useless trash and contribute zero value to this project.", "harassment", True, 2),

        # HATE SPEECH (15)
        ("People from that country are subhuman savages who shouldn't be allowed in our society.", "hate_speech", True, 3),
        ("Those people are genetic garbage and belong in cages, not in public offices.", "hate_speech", True, 3),
        ("All members of that religion are inherently violent terrorists and should be deported.", "hate_speech", True, 3),
        ("We need to purge our country of these parasites before they destroy our culture.", "hate_speech", True, 3),
        ("They are an inferior race that drags down civilized society everywhere they go.", "hate_speech", True, 3),
        ("Women are naturally incapable of logical thinking and shouldn't work in engineering.", "hate_speech", True, 3),
        ("Those disgusting deviants should be rounded up and locked away from normal people.", "hate_speech", True, 3),
        ("They are like cockroaches invading our neighborhood. Time to eradicate them.", "hate_speech", True, 3),
        ("Disabled people are just a drain on society's resources and offer nothing.", "hate_speech", True, 3),
        ("Send every single one of those immigrants back in body bags where they belong.", "hate_speech", True, 3),
        ("Their entire demographic is biologically criminal and untrustworthy.", "hate_speech", True, 3),
        ("They don't deserve human rights; exterminating them would do the world a favor.", "hate_speech", True, 3),
        ("We will never accept your filthy kind here. You are vermin.", "hate_speech", True, 3),
        ("Total genocide of that ethnic group is the only permanent solution.", "hate_speech", True, 3),
        ("No wonder people hate your group. You are pure evil and disease.", "hate_speech", True, 3),

        # PROFANITY (15)
        ("What the actual fuck is wrong with this goddamn build pipeline today?", "profanity", True, 1),
        ("Holy shit, that benchmark result is totally insane!", "profanity", True, 1),
        ("This damn laptop just crashed again and wiped out my entire branch.", "profanity", True, 1),
        ("That was such a bullshit penalty call by the referee in the second half.", "profanity", True, 1),
        ("Fuck yeah, we finally closed the release ticket ahead of schedule!", "profanity", True, 1),
        ("Damn, that server outage cost us thousands of dollars in lost traffic.", "profanity", True, 1),
        ("This code is a giant pile of shit, who approved this PR?", "profanity", True, 1),
        ("What a fucking mess of spaghetti code in the legacy auth module.", "profanity", True, 1),
        ("I'm so pissed off right now, the airline cancelled my flight with zero notice.", "profanity", True, 1),
        ("Damn it, I forgot to run database migrations before deploying to staging.", "profanity", True, 1),
        ("Holy crap, did you see the new pricing tier? It is ridiculously expensive.", "profanity", True, 1),
        ("The wifi here is bloody awful and keeps dropping my ssh session.", "profanity", True, 1),
        ("What the hell happened to our staging environment overnight?", "profanity", True, 1),
        ("That was a badass presentation, awesome job on the live demo.", "profanity", True, 1),
        ("Damn, that was a brutal interview loop with four coding rounds.", "profanity", True, 1),
    ]

    cases = []
    for i, (text, cat, is_viol, score) in enumerate(samples[:count]):
        cases.append({
            "id": f"mod-{i+1:03d}",
            "domain": "trust_and_safety",
            "state": text,
            "questions": questions_def,
            "labels": {
                "violation_type": cat,
                "policy_violation": is_viol,
                "enforcement_action": score
            }
        })
    return cases


def build_ecommerce_support_cases(count=60):
    questions_def = {
        "routing": {
            "type": "choice",
            "instructions": "Which customer support team should handle this order inquiry?",
            "criteria": {
                "shipping": "Tracking deliveries, shipment delays, lost parcels, or carrier issues.",
                "returns_defects": "Damaged goods, defective items, exchange requests, and warranty claims.",
                "billing": "Double charges, invoice errors, promo code failures, or refund status.",
                "tech_support": "Account login, password resets, website glitches, or payment checkout errors."
            }
        },
        "urgent_escalation": {
            "type": "noul",
            "instructions": "Does this customer require urgent human escalation or immediate resolution?"
        },
        "churn_risk": {
            "type": "score",
            "instructions": "How severe is the customer's frustration and risk of churn?",
            "criteria": [
                "Low: Calm, informational inquiry or routine question.",
                "Moderate: Minor inconvenience; customer remains patient.",
                "High: Significant frustration; delayed delivery or product issue.",
                "Critical: Extreme anger; threatening legal action, chargeback, or public cancellation."
            ]
        }
    }

    # 60 balanced ecommerce support cases across the 4 routing teams (15 per team)
    items = [
        # Shipping (15)
        ("My package was supposed to arrive three days ago but tracking has not updated since Tuesday.", "shipping", False, 1),
        ("The tracking says delivered to porch, but I was home all day and nothing was left. Please locate my parcel.", "shipping", True, 2),
        ("I need to change my shipping address from 14 Oak St to 22 Pine Ave before the warehouse ships my order.", "shipping", True, 1),
        ("Can you tell me what carrier is delivering order #98231? I need to give them gate access instructions.", "shipping", False, 0),
        ("This is the third time this month your delivery driver tossed my fragile package over the back fence!", "shipping", True, 3),
        ("Tracking says 'Held in Customs - Pending Tax Payment'. How do I clear this fee?", "shipping", False, 1),
        ("Is international expedited shipping available to South Korea for the monitor order?", "shipping", False, 0),
        ("My order has been stuck in the distribution hub for over 10 days with no movement. Is it lost?", "shipping", True, 2),
        ("The courier marked delivery attempted, but nobody rang the bell or left a delivery notice card.", "shipping", False, 1),
        ("I ordered next-day priority delivery for my daughter's birthday tomorrow. Will it arrive by 2 PM?", "shipping", True, 2),
        ("Can I request signature-required delivery for the high-value jewelry package?", "shipping", False, 0),
        ("The shipping confirmation email didn't include a tracking number. Could you send it over?", "shipping", False, 0),
        ("Two weeks of delays and empty promises! I demand you ship a replacement right now or refund me!", "shipping", True, 3),
        ("Can packages be held at the local post office for customer pickup instead of home delivery?", "shipping", False, 0),
        ("Driver marked delivered, but the photo shows a completely different house and porch. That's not my home.", "shipping", True, 2),

        # Returns & Defects (15)
        ("The coffee maker I received has a shattered water reservoir right out of the box. Please send a replacement.", "returns_defects", True, 2),
        ("I ordered size 10 running shoes, but the box contained size 8. How do I start an exchange?", "returns_defects", False, 1),
        ("The OLED television has multiple dead pixel lines running down the center of the display.", "returns_defects", True, 2),
        ("What is your standard return policy window for unworn apparel with tags still attached?", "returns_defects", False, 0),
        ("The leather jacket is beautiful, but the sleeves are slightly too long. Can I return it for store credit?", "returns_defects", False, 0),
        ("This blender stopped spinning after exactly two uses. Burning smell coming from motor. Very dangerous!", "returns_defects", True, 3),
        ("How long does it take for a return label to be generated after requesting an RMA online?", "returns_defects", False, 0),
        ("I dropped off my return package at the drop box last Monday. When will my exchange order be dispatched?", "returns_defects", False, 1),
        ("The headphones only play audio in the left earbud. Factory reset did not fix the problem.", "returns_defects", False, 1),
        ("Your company sold me a clearly counterfeit perfume bottle. This is fraud and I am filing a formal complaint!", "returns_defects", True, 3),
        ("I received two blue shirts instead of one blue and one white shirt as ordered in invoice #4421.", "returns_defects", False, 1),
        ("Is return shipping free if the item was defective on delivery?", "returns_defects", False, 0),
        ("The wooden dining table arrived with a deep 6-inch gouge on the top surface. Extremely disappointed.", "returns_defects", True, 2),
        ("Can I return an online order to a physical retail store location for immediate refund?", "returns_defects", False, 0),
        ("Third defective replacement in a row! You guys have zero quality control. I am never buying from you again!", "returns_defects", True, 3),

        # Billing (15)
        ("I was charged twice for order #88412 on my Visa card. Please refund the duplicate transaction.", "billing", True, 2),
        ("Why was a 15 dollar handling fee added to my statement when the cart advertised free shipping?", "billing", False, 1),
        ("My promo code SAVE20 was applied at checkout, but the final invoice charged the full price.", "billing", False, 1),
        ("Could you please email me a formal VAT invoice with company tax registration details for order #7129?", "billing", False, 0),
        ("You charged my credit card without my authorization after I cancelled the subscription three weeks ago!", "billing", True, 3),
        ("I returned my item two weeks ago and tracking confirmed receipt, but the refund hasn't hit my bank account.", "billing", True, 2),
        ("What payment methods are supported for split billing across multiple corporate cards?", "billing", False, 0),
        ("My gift card balance shows zero even though I only used 20 dollars of the 100 dollar balance.", "billing", False, 1),
        ("If you do not refund this unauthorized charge within 24 hours, I am initiating a bank chargeback.", "billing", True, 3),
        ("Can I change the billing address on my monthly recurring auto-shipment?", "billing", False, 0),
        ("Why does my bank statement show a charge from ACME-CORP when I purchased from your store?", "billing", False, 0),
        ("The receipt shows a sales tax rate of 10%, but our state tax rate is only 6.5%. Please correct this.", "billing", False, 1),
        ("Your agent promised a 50 dollar courtesy credit for the delayed sofa, but it was never applied.", "billing", True, 2),
        ("Can I get an itemized price breakdown of the customs duties and taxes included in my order?", "billing", False, 0),
        ("You double billed my account for 1,200 dollars and now my card is overdrawn. Fix this immediately!", "billing", True, 3),

        # Tech Support (15)
        ("Every time I click 'Place Order', the checkout page reloads with a generic error code ERR_PAYMENT_GATEWAY.", "tech_support", True, 2),
        ("I am unable to reset my password because the verification email never arrives in my inbox.", "tech_support", False, 1),
        ("The mobile app keeps crashing whenever I tap on the 'My Orders' tab on iOS 18.", "tech_support", False, 1),
        ("How do I update my two-factor authentication phone number after getting a new SIM card?", "tech_support", False, 0),
        ("Your website is completely down during the flash sale! Nobody can complete purchases!", "tech_support", True, 3),
        ("Items saved in my cart disappear every time I log out and log back in from another browser.", "tech_support", False, 1),
        ("I'm getting an 'Invalid Session Token' error when trying to access my loyalty reward points.", "tech_support", False, 1),
        ("Does your website support Apple Pay on desktop Chrome or only Safari?", "tech_support", False, 0),
        ("I cannot upload the photo of the damaged package; the file upload button is completely unresponsive.", "tech_support", False, 1),
        ("A security warning popped up saying your checkout certificate expired. Is customer payment data compromised?", "tech_support", True, 3),
        ("How do I delete my payment card details saved in the autofill account settings?", "tech_support", False, 0),
        ("The search filter for 'In Stock' items is still showing dozens of out-of-stock products.", "tech_support", False, 0),
        ("My account has been locked due to too many failed attempts, but I never tried logging in today!", "tech_support", True, 2),
        ("Can I link multiple email addresses to a single customer rewards account?", "tech_support", False, 0),
        ("The site just debited my Apple Pay but showed an error screen and generated no order confirmation number!", "tech_support", True, 3),
    ]

    cases = []
    for i, (text, team, is_urg, risk) in enumerate(items[:count]):
        cases.append({
            "id": f"retail-{i+1:03d}",
            "domain": "ecommerce_support",
            "state": text,
            "questions": questions_def,
            "labels": {
                "routing": team,
                "urgent_escalation": is_urg,
                "churn_risk": risk
            }
        })
    return cases


def build_ag_news_cases(count=60):
    url = "https://raw.githubusercontent.com/mhjabreel/CharCnn_Keras/master/data/ag_news_csv/test.csv"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    data = urllib.request.urlopen(req).read().decode("utf-8")
    reader = csv.reader(io.StringIO(data))
    all_rows = list(reader)

    # Class 1: World, 2: Sports, 3: Business, 4: Sci/Tech
    class_map = {
        "1": "world",
        "2": "sports",
        "3": "business",
        "4": "scitech"
    }

    questions_def = {
        "topic": {
            "type": "choice",
            "instructions": "What primary news category does this article snippet belong to?",
            "criteria": {
                "business": "Corporate earnings, markets, trade, economic policy, and mergers.",
                "scitech": "Technology, software, gadgets, space, internet, and scientific discoveries.",
                "world": "International politics, diplomacy, conflicts, elections, and global events.",
                "sports": "Athletics, tournaments, professional leagues, matches, and player transfers."
            }
        },
        "financial_relevance": {
            "type": "noul",
            "instructions": "Does this news story have direct financial, corporate, or stock market relevance?"
        },
        "breaking_urgency": {
            "type": "score",
            "instructions": "How urgent or high-impact is this news development?",
            "criteria": [
                "Routine or feature story; low immediate market/editorial urgency.",
                "Standard event coverage or scheduled match/product announcement.",
                "High-impact developing story; major geopolitical or market development.",
                "Breaking emergency; major disaster, war, market crash, or sudden CEO resignation."
            ]
        }
    }

    by_class = {"world": [], "sports": [], "business": [], "scitech": []}
    for r in all_rows:
        cid = r[0]
        cat = class_map.get(cid)
        if cat and len(r) >= 3:
            title = r[1].strip()
            desc = r[2].strip()
            text = f"{title}. {desc}"
            by_class[cat].append((text, cat))

    cases_per_class = count // 4 # 15 each
    cases = []
    for cat, items in by_class.items():
        random.shuffle(items)
        for text, c in items[:cases_per_class]:
            is_financial = (c == "business")
            if c == "business":
                urgency = 2 if ("crash" in text.lower() or "soar" in text.lower() or "plunge" in text.lower()) else 1
            elif c == "world":
                urgency = 3 if ("attack" in text.lower() or "war" in text.lower() or "blast" in text.lower()) else 2
            elif c == "scitech":
                urgency = 2 if ("vulnerability" in text.lower() or "breakthrough" in text.lower()) else 1
            else:
                urgency = 1 if ("final" in text.lower() or "cup" in text.lower() or "win" in text.lower()) else 0

            cases.append({
                "id": f"news-{len(cases)+1:03d}",
                "domain": "news_topics",
                "state": text,
                "questions": questions_def,
                "labels": {
                    "topic": c,
                    "financial_relevance": is_financial,
                    "breaking_urgency": urgency
                }
            })

    return cases[:count]


def main():
    print("Building 300-case diverse benchmark suite...")

    print("1/5 Fetching & building Banking77 cases (60)...")
    banking = build_banking77_cases(60)
    print(f"    Built {len(banking)} banking cases.")

    print("2/5 Fetching & building CLINC150 conversational assistant cases (60)...")
    clinc = build_clinc_cases(60)
    print(f"    Built {len(clinc)} assistant cases.")

    print("3/5 Building Trust & Safety moderation cases (60)...")
    moderation = build_moderation_cases(60)
    print(f"    Built {len(moderation)} moderation cases.")

    print("4/5 Building E-Commerce Support triage cases (60)...")
    ecommerce = build_ecommerce_support_cases(60)
    print(f"    Built {len(ecommerce)} retail support cases.")

    print("5/5 Fetching & building AG News business & tech cases (60)...")
    news = build_ag_news_cases(60)
    print(f"    Built {len(news)} news cases.")

    all_cases = banking + clinc + moderation + ecommerce + news
    print(f"\nTotal curated cases: {len(all_cases)}")
    assert len(all_cases) == 300, f"Expected 300 cases, got {len(all_cases)}"

    out_file = Path("benchmarks/diverse_300.jsonl")
    with open(out_file, "w", encoding="utf-8") as f:
        for c in all_cases:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")

    print(f"Successfully saved {len(all_cases)} cases to {out_file}")


if __name__ == "__main__":
    main()
