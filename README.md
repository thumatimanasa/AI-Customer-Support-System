# Hiver SDE Intern Assignment — AI Customer Support for American Airlines

## 1. Problem Framing

This project explores an AI-assisted customer-support system using the Customer Support on Twitter dataset.

The system takes a customer message and performs four steps:

1. Detect the customer's support intent.
2. Retrieve similar historical customer-support interactions.
3. Draft a concise reply grounded in historical resolutions.
4. Decide whether the case can be safely auto-handled or should be escalated.

The primary design principle is **safe automation rather than maximizing automation volume**.

## 2. Dataset and Brand Selection

Dataset: **Customer Support on Twitter**

Source: Kaggle `thoughtvector/customer-support-on-twitter`

The dataset contains customer-support conversations between users and brands.

### Brand selection

Several support-heavy brands were profiled before selecting the final brand.

**AmericanAir** was selected based on usable support-pair volume and pairing quality.

- Support replies: **36,598**
- Required customer messages: **36,524**
- Retrieved customer messages: **36,457**
- Final usable customer-support pairs: **36,531**

The selection was based on usable support data rather than simply choosing the largest brand.

## 3. Customer → Support Pair Construction

A support interaction was defined as:

`customer tweet → brand support reply`

where the support reply is an outbound brand tweet whose `in_response_to_tweet_id` points to the customer's tweet.

Tweet IDs were normalized before joining because some IDs appeared with a `.0` suffix after CSV parsing.

## 4. Intent Taxonomy

Exploratory keyword analysis and TF-IDF clustering were used to identify recurring support topics.

The final taxonomy contains 13 intents:

- `flight_delay_status`
- `cancellation_schedule`
- `rebooking_itinerary`
- `baggage`
- `seat`
- `booking`
- `checkin_boarding_gate`
- `payment_fees_refund`
- `loyalty`
- `onboard_services`
- `accessibility`
- `lost_found`
- `general_complaint_or_other`

A general/social category was retained because the source contains acknowledgements, praise, complaints and messages that do not always map to an operational support intent.

## 5. Temporal Evaluation Split

To reduce temporal leakage, interactions were divided chronologically.

- Historical/evidence period: **29,224 interactions**
- Evaluation period: **7,307 interactions**
- Split: approximately **80/20 temporal**
- Cutoff: **2017-11-21 13:48:37 UTC**

The evaluation examples therefore occur after the historical evidence used by the system.

## 6. Golden Evaluation Set

A hand-labelled golden evaluation set of **220 examples** was created.

The sample was intentionally constructed from topic buckets so that important support categories and difficult cases were represented.

Each example contains:

- Customer message
- Human intent
- Safe-to-auto-handle label
- Evidence sufficiency label
- Escalation reason
- Expected reply points

Human automation labels:

- Safe to auto-handle: **54 / 220**
- Escalate: **166 / 220**

Therefore, the evaluation set is **not a naturally representative production distribution**.

## 7. System Design

The system consists of four main stages:

1. Intent classification
2. Intent-aware historical retrieval
3. Grounded reply generation
4. Safety and escalation decision

### Intent classifier

A TF-IDF nearest-centroid classifier was trained using weak keyword-derived labels from the historical period.

A phrase-first hybrid was also tested.

### Historical retrieval

TF-IDF retrieval with unigram/bigram features finds similar historical customer messages.

The final retrieval stage restricts candidates to the predicted intent.

### Reply generation

Replies are grounded in retrieved historical support responses.

The generator is instructed not to invent policies, compensation, timelines, URLs, phone numbers, guarantees or case status.

### Safety gate

The system combines:

- Intent confidence
- Historical retrieval similarity
- Evidence sufficiency
- Higher-risk intent rules

Higher-risk areas such as accessibility, lost/found, payment/refund, cancellation and rebooking receive stricter handling.
## 8. Baselines

### Baseline 1 — Always Escalate

The first baseline always escalates and returns a generic support response.

| Metric | Always Escalate |
|---|---:|
| Cases | 220 |
| Auto-handled | 0 |
| Escalated | 220 |
| Raw decision accuracy | 75.45% |
| Mean reply-point coverage | 0.0073 |

The 75.45% raw decision accuracy is mainly a consequence of the evaluation distribution: 166/220 cases are labelled for escalation. Therefore, this is not used as the headline performance metric.

### Baseline 2 — TF-IDF Historical Retrieval

The second baseline retrieves the most similar historical customer interaction and uses its historical support response as the reply.

| Metric | TF-IDF Retrieval |
|---|---:|
| Cases | 220 |
| Auto-handled | 0 |
| Escalated | 220 |
| Raw decision accuracy | 75.45% |
| Mean retrieval similarity | 0.2615 |
| Mean reply-point coverage | 0.0150 |

This improves evidence retrieval relative to the trivial response, but lexical similarity alone can confuse closely related operational issues.

## 9. Final System Evaluation

### Intent Classification

The final TF-IDF intent classifier achieved:

- Intent accuracy: **56.36%**
- Errors: **96 / 220**
- Mean confidence: **0.1528**

A phrase-first hybrid improved intent accuracy to **58.64%**, but the improvement was modest.

This indicates that intent routing is a major bottleneck.

### Intent-Aware Retrieval

The final retrieval corpus contains **28,781 historical interactions**.

Mean top-1 retrieval similarity:

**0.1921**

The retrieved candidate is restricted to the predicted intent.

The retrieved-intent match diagnostic should not be interpreted as independent retrieval accuracy because it is dependent on the upstream intent prediction.

## 10. Safety Gate Results

### Version 1

The first safety gate allowed automation for sufficiently confident, sufficiently similar, lower-risk cases.

| Metric | Result |
|---|---:|
| Auto-handled | 23 / 220 |
| Escalated | 197 / 220 |
| Automation precision | 21.74% |
| Safe automation coverage | 9.26% |
| Unsafe auto rate | 8.18% |
| Escalation recall | 89.16% |
| Automation F1 | 12.99% |
| Raw decision accuracy | 69.55% |

There were **18 unsafe auto-handled cases**.

The main lesson is that moderate TF-IDF similarity and intent confidence do not reliably imply that historical evidence is actionable.

### Version 2 — Stricter Gate

A stricter threshold configuration was tested.

| Metric | Result |
|---|---:|
| Auto-handled | 0 / 220 |
| Escalated | 220 / 220 |
| Unsafe auto rate | 0% |
| Escalation recall | 100% |
| Raw decision accuracy | 75.45% |

This configuration is extremely conservative and eliminates automation coverage.

Threshold calibration showed that requiring approximately 90% automation precision produced only **1 automatically handled case out of 220** in the tested threshold grid.

This indicates that threshold tightening alone does not solve the underlying routing and retrieval problems.

## 11. Evidence Sufficiency Evaluation

An independent human review was conducted on **100 evaluation examples**.

The reviewer independently labelled whether the historical evidence was sufficient to safely support a useful response.

Human labels:

- Evidence sufficient: **37**
- Evidence insufficient: **63**

An LLM evidence judge was then evaluated against these human labels.

### Agreement

**81% agreement (81 / 100)**

| | LLM Insufficient | LLM Sufficient |
|---|---:|---:|
| Human Insufficient | 62 | 1 |
| Human Sufficient | 18 | 19 |

The LLM judge was more conservative than the human reviewer:

- Human sufficient: 37%
- LLM sufficient: 20%

This metric is reported as **agreement**, not objective accuracy, because the human label itself is a reviewer judgement.

## 12. Top 5 Failure Modes

### 1. Intent overlap between related operational issues

**Example:** Eval 1 contains a schedule/check-in discrepancy, but the classifier routed it to check-in/boarding rather than cancellation/schedule.

**Hypothesis:** Related airline support intents share vocabulary such as flight, check-in, time, gate, and boarding.

### 2. Complex multi-issue complaints

**Example:** Eval 212 combines check-in failure, a two-hour wait, lack of staff, imminent boarding, and inability to check bags.

**Hypothesis:** A single-label classifier loses secondary issues and urgency.

### 3. Semantic similarity does not guarantee actionable evidence

**Example:** Short conversational messages such as acknowledgements can retrieve historically similar but operationally irrelevant conversations.

**Hypothesis:** Lexical similarity does not capture conversational state, whether an issue is already resolved, or whether the historical response actually answers the current message.

### 4. Weak evidence for high-risk/specialized cases

**Example:** Eval 9 concerns wheelchair assistance, but nearby historical evidence does not directly resolve the accessibility request.

**Hypothesis:** Specialized intents are sparse in the selected corpus and require stricter evidence requirements.

### 5. Positive/social messages confuse an issue-oriented taxonomy

**Example:** Eval 114 is positive feedback for a gate agent, but the classifier routes it as an operational support case.

**Hypothesis:** The source contains praise, acknowledgements, and social conversation that do not always represent unresolved support issues.

## 13. What Is Misleading About My Headline Number?

The strongest headline-style number in the evaluation is the **81% evidence judge-human agreement**.

It should **not** be interpreted as end-to-end system accuracy.

Important caveats:

1. The 100-case evidence review is a subset of the 220-case golden evaluation set.
2. The golden set intentionally oversamples important support topics.
3. Human labels are reviewer judgements rather than objective resolution ground truth.
4. The LLM judge is more conservative than the human reviewer.
5. Intent accuracy is only 56.36%, so evidence quality is affected by upstream routing.
6. The v1 automation precision of 21.74% is based on only 23 automated cases and should not be treated as a production estimate.
7. Always-escalate obtains 75.45% raw decision accuracy because the golden set contains many escalation cases.

The numbers are therefore best viewed as **diagnostic evaluation results**, not production performance estimates.
## 14. One-Week Improvement Plan

| Day | Focus |
|---|---|
| Day 1 | Refine taxonomy boundaries: cancellation vs delay, booking vs seat, payment/refund vs operational |
| Day 2 | Add conversational-state handling for acknowledgements, praise, and social messages |
| Day 3 | Replace pure TF-IDF retrieval with hybrid lexical + semantic retrieval and reranking |
| Day 4 | Add multi-intent extraction and urgent/high-risk prioritization |
| Day 5 | Strengthen evidence requirements for financial, accessibility, lost/found, cancellation, and rebooking cases |
| Day 6 | Build a larger stratified evaluation set covering social, ambiguous, high-risk, and multi-intent cases |
| Day 7 | Re-run end-to-end evaluation and revalidate automation precision and safe coverage |

## 15. Decision Log

Key non-obvious decisions are documented in `evaluation/decision_log_americanair.csv`.

Important decisions include:

- Selecting AmericanAir based on usable support-pair quality rather than raw volume.
- Using a temporal split to reduce leakage.
- Keeping a general/social intent.
- Including an always-escalate baseline.
- Restricting retrieval to the predicted intent.
- Using both intent confidence and retrieval similarity.
- Applying deterministic escalation rules for high-risk intents.
- Separately evaluating evidence sufficiency.
- Using an independent 100-case evidence review.
- Avoiding raw decision accuracy as the headline metric.


## 16. Reproducibility

The project was developed and tested in **Google Colab using Python**.

Core libraries used include:

- `pandas`
- `numpy`
- `scikit-learn`
- `matplotlib`
- `openai`

The source dataset is **not included in this repository** because of its size.

Download the **Customer Support on Twitter** dataset from Kaggle:

https://www.kaggle.com/thoughtvector/customer-support-on-twitter

The dataset contains the file:

```text
twcs.csv
```
### Reproducing the Reported Results

The main evaluation metrics can be reproduced **without an API key** using the committed evaluation artifacts.

From the repository root, run:

```bash
python src/reproduce_results.py
```
The script reads the evaluation files stored under `evaluation/` and reports:

- Golden evaluation set size
- Intent classification accuracy
- Safety-gate metrics
- Automation precision
- Safe automation coverage
- Unsafe automation rate
- Evidence judge-human agreement
- Stricter safety-gate result

The clean analysis notebook is available at:

```text
src/Hiver_SDE_Support_Agent_Clean.ipynb
```

## 17. Repository Structure
```text

hiver_submission/
│
├── README.md
├── requirements.txt
│
├── src/
│   ├── Hiver_SDE_Support_Agent_Clean.ipynb
│   └── reproduce_results.py
│
└── evaluation/
    ├── golden_eval_americanair_220_FINAL.csv
    ├── baseline1_trivial_americanair.csv
    ├── baseline2_tfidf_americanair.csv
    ├── intent_classifier_eval_americanair.csv
    ├── intent_aware_retrieval_americanair.csv
    ├── evidence_safety_gate_americanair.csv
    ├── improved_safety_gate_americanair.csv
    ├── safety_threshold_calibration_americanair.csv
    ├── evidence_judge_human_agreement_100.csv
    ├── llm_evidence_judge_100_checkpoint.csv
    ├── top5_failure_modes_americanair.csv
    ├── decision_log_americanair.csv
    ├── one_week_improvement_plan_americanair.csv
    └── headline_number_caveat.txt
```
## 18. Final Takeaway

The experiment shows that a support automation system can be constructed from historical customer-support interactions, but the main challenge is not simply generating fluent replies.

The critical bottlenecks are:

**intent routing → actionable evidence retrieval → safe automation**

The evaluation therefore prioritizes evidence quality and escalation safety rather than maximizing the percentage of cases automatically handled.

## 19. Evaluation Artifacts

The `evaluation/` directory contains the complete supporting artifacts:

- Golden evaluation set
- Trivial baseline
- TF-IDF retrieval baseline
- Intent classifier evaluation
- Intent-aware retrieval results
- Safety-gate results
- Threshold calibration
- Independent human evidence review
- LLM evidence-judge comparison
- Failure-mode analysis
- Decision log
- One-week improvement plan
- Headline-number caveat