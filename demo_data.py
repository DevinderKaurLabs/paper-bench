"""Five fully worked demo projects for Paper Bench.

Every paper here is a real, published paper. The cards are written from
knowledge of each paper (not from its full text), so each card carries a
"knowledge" confidence label, and findings carry their own labels.
"""
import hashlib


def P(num, title, authors, year, venue, one_liner, summary, method, findings, limits,
      borrow, weekend, score, why, terms, knowledge="Certain"):
    return {
        "id": "demo-" + hashlib.md5(title.encode()).hexdigest()[:10],
        "num": num, "title": title, "authors": authors, "year": year,
        "origin": "knowledge", "source": "Claude's knowledge", "text": "",
        "card": {
            "title": title, "authors": authors, "year": year, "venue": venue,
            "one_liner": one_liner, "plain_summary": summary, "method": method,
            "key_findings": [{"claim": c, "confidence": k} for c, k in findings],
            "limitations": limits, "builder_takeaways": borrow, "weekend_test": weekend,
            "relevance": {"score": score, "why": why},
            "key_terms": [{"term": t, "meaning": m} for t, m in terms],
            "knowledge": knowledge,
        },
    }


def sug(title, authors, year, why, confidence="Certain"):
    return {"title": title, "authors": authors, "year": year, "why": why, "confidence": confidence}


def sol(name, pitch, grounded, steps, win, risks, mvp, hyp, metric, success, drop, effort, conf):
    return {"name": name, "pitch": pitch, "grounded_in": grounded, "how_it_works": steps,
            "why_it_could_win": win, "risks": risks, "mvp": mvp,
            "experiment": {"hypothesis": hyp, "metric": metric, "success_threshold": success,
                           "change_our_mind": drop},
            "effort": effort, "confidence": conf}


# ---------------------------------------------------------------- 1. Loyalty churn
LOYALTY = {
    "id": "demo-loyalty", "demo": True,
    "name": "Loyalty lapse: who to save, and with what",
    "problem": ("Our retail loyalty programme has 400k members. Most buy rarely and irregularly, so nobody "
                "ever 'cancels'. We spend on win-back offers every month but can't tell who is really "
                "about to lapse, or whether the offers change anything."),
    "context": "GCC retail, 2 years of transactions, campaign logs in the CRM.",
    "constraints": "Python team of 2, 6 weeks, no new tooling budget.",
    "map": {
        "reframed_problem": ("Two linked research questions. First, how do we estimate whether a member is still "
                             "active when churn is never observed? Second, whom should we target so the offer "
                             "changes behaviour, rather than rewarding people who would have stayed anyway?"),
        "why_hard": ("In non-contractual retail a quiet member may be gone or simply between purchases, and "
                     "the members most likely to leave are not always the ones an offer can persuade."),
        "sub_questions": [
            "How do we estimate the probability a member is still active from purchase timing alone?",
            "Should we predict churn risk, or the response to a retention offer (uplift)?",
            "How do we judge a churn model in money rather than accuracy?",
            "How much transaction history do these methods need?",
        ],
        "concepts": [
            {"term": "Non-contractual setting", "meaning": "Customers leave silently; you only see when they buy."},
            {"term": "BTYD models", "meaning": "'Buy Till You Die' models (Pareto/NBD, BG/NBD) that estimate purchase rate and dropout."},
            {"term": "P(alive)", "meaning": "The probability a customer has not yet dropped out."},
            {"term": "Uplift modelling", "meaning": "Predicts the change in behaviour caused by an action, not the behaviour itself."},
            {"term": "Profit curve", "meaning": "Expected campaign profit at each targeting depth."},
        ],
        "search_queries": [
            {"query": "BG/NBD non-contractual customer base", "purpose": "Core models for silent churn"},
            {"query": "uplift modeling retention campaign targeting", "purpose": "Who to target, not just who is at risk"},
            {"query": "profit driven churn prediction evaluation", "purpose": "Measuring models in money"},
            {"query": "customer lifetime value modeling review", "purpose": "Valuing who is worth saving"},
        ],
        "landmark_papers": [
            sug("Counting Your Customers: Who Are They and What Will They Do Next?", "Schmittlein, Morrison, Colombo", "1987",
                "Introduced Pareto/NBD for customers who leave silently."),
            sug("“Counting Your Customers” the Easy Way: An Alternative to the Pareto/NBD Model", "Fader, Hardie, Lee", "2005",
                "BG/NBD: same idea, far easier to fit."),
            sug("Retention Futility: Targeting High-Risk Customers Might Be Ineffective", "Ascarza", "2018",
                "Targeting by risk can waste budget; target by predicted response."),
            sug("New insights into churn prediction in the telecommunication sector: A profit driven data mining approach",
                "Verbeke, Dejaeger, Martens, Hur, Baesens", "2012", "Evaluates churn models by campaign profit.", "Likely"),
            sug("Modeling Customer Lifetime Value", "Gupta, Hanssens, Hardie, Kahn, Kumar, Lin, Ravishanker, Sriram", "2006",
                "Broad review of CLV approaches, useful for valuing who to save."),
        ],
        "adjacent_fields": [
            {"field": "Causal inference", "why": "Uplift is a treatment-effect problem."},
            {"field": "Survival analysis", "why": "Time-to-lapse framing with censored members."},
        ],
    },
    "papers": [
        P(1, "Counting Your Customers: Who Are They and What Will They Do Next?", "Schmittlein, Morrison, Colombo", "1987",
          "Management Science",
          "A model that estimates whether a quiet customer is still active, using only how often and how recently they bought.",
          ("Customers buy at their own steady rate while active and drop out at some unseen moment. Because rates differ "
           "across people, the model learns the spread of rates across the whole base, then works out each person's chance "
           "of still being active and their expected future purchases."),
          "Poisson purchasing while active, exponential lifetimes, gamma-distributed rates across customers (Pareto/NBD).",
          [("Recency, frequency and customer age are sufficient to estimate activity and future purchases under the model's assumptions.", "Certain"),
           ("A long gap is far more worrying for a frequent buyer than for a rare one.", "Certain")],
          ["Harder to estimate than later alternatives", "Assumes stable purchase rates", "Ignores spend and marketing actions"],
          ["Your input table is just recency, frequency and tenure per member", "Use P(alive) as a feature for later models"],
          "Fit Pareto/NBD with the PyMC-Marketing or lifetimes library on 12 months of data and check calibration on a 3-month holdout.",
          4, "Directly models silent lapse in loyalty data.",
          [("P(alive)", "Probability the customer has not dropped out."), ("Recency", "Time since the last purchase.")]),
        P(2, "“Counting Your Customers” the Easy Way: An Alternative to the Pareto/NBD Model", "Fader, Hardie, Lee", "2005",
          "Marketing Science",
          "Same goal as Pareto/NBD, but dropout can only happen right after a purchase, which makes the model far easier to fit.",
          ("The BG/NBD model changes one assumption about when customers can leave. That small change turns a hard "
           "estimation problem into one a spreadsheet can handle, with forecasts close to the original model."),
          "Beta-geometric dropout after each purchase plus NBD purchasing, fitted by maximum likelihood on recency/frequency summaries.",
          [("Forecast accuracy is close to Pareto/NBD at much lower computational cost.", "Likely")],
          ["Customers with no repeat purchase are treated as certainly active", "Same stable-rate assumptions"],
          ["Fits in minutes in Python, a strong default baseline", "Pair with Gamma-Gamma for spend to get CLV"],
          "Compare BG/NBD against a gradient-boosted classifier on 'no purchase in the next 90 days'. If the simple model is close, ship it first.",
          5, "Fastest route to a defensible baseline.",
          [("Gamma-Gamma", "Companion model for average spend per transaction.")]),
        P(3, "Retention Futility: Targeting High-Risk Customers Might Be Ineffective", "Ascarza", "2018",
          "Journal of Marketing Research",
          "Sending retention offers to the highest-risk customers can waste money; target the ones most likely to respond.",
          ("Using retention field experiments, the paper shows that the people most likely to leave are often not the people "
           "an offer persuades to stay. Ranking customers by predicted response to the offer cuts churn more for the same budget."),
          "Randomised retention campaigns; compares targeting by churn risk with targeting by predicted treatment effect (uplift).",
          [("Customers with the highest churn risk were often not those whose behaviour the campaign changed.", "Certain"),
           ("Uplift-based targeting reduced churn more than risk-based targeting at equal budget.", "Likely")],
          ["Needs randomised treatment/control history", "Uplift models are noisy on small samples"],
          ["Hold out a random control group in every retention campaign from now on", "Rank by expected incremental profit, not risk"],
          "Take one past campaign with a control group, fit a T-learner uplift model, and compare top-decile uplift with top-decile risk.",
          5, "Changes what the targeting model should predict.",
          [("Uplift", "Outcome if treated minus outcome if not treated."), ("T-learner", "Two models, one per group, whose difference estimates uplift.")]),
        P(4, "New insights into churn prediction in the telecommunication sector: A profit driven data mining approach",
          "Verbeke, Dejaeger, Martens, Hur, Baesens", "2012", "European Journal of Operational Research",
          "Judge churn models by how much money the retention campaign would make, not by accuracy.",
          ("The authors benchmark many classifiers and show that a profit-based measure can rank them differently from AUC. "
           "They also find that simpler, readable rule models can be competitive."),
          "Benchmark of classifiers across telecom datasets, evaluated with a profit-based measure.",
          [("Model rankings change when switching from AUC to profit-based measures.", "Likely"),
           ("Readable rule-based models can be competitive with complex ones.", "Likely")],
          ["Telecom is contractual, so churn is observed; retail differs", "Profit inputs must be assumed"],
          ["Add a profit curve to every model report: contact cost, offer cost, CLV, acceptance rate", "Set the cut-off where profit peaks, not at 0.5"],
          "Recompute your current model's results as a profit curve and see whether the best targeting depth moves.",
          3, "Useful evaluation lens; the setting differs from retail.",
          [("Profit curve", "Expected campaign profit at each targeting depth.")], knowledge="Likely"),
    ],
    "synthesis": {
        "state_of_field": ("Three strands fit together as a pipeline. BTYD models [P1][P2] estimate who is still active from "
                           "purchase timing. Profit-based evaluation [P4] judges models in money. Causal targeting [P3] shows "
                           "risk is the wrong thing to rank by."),
        "approaches": [
            {"name": "BTYD activity models", "papers": ["P1", "P2"], "how": "Fit purchase-rate and dropout distributions from recency and frequency.",
             "strengths": "Few inputs, interpretable, works with short history", "weaknesses": "Ignores marketing actions and spend", "data_needs": "Purchase dates per member, about a year"},
            {"name": "Uplift targeting", "papers": ["P3"], "how": "Model the outcome difference between treated and control members.",
             "strengths": "Spends budget where it changes behaviour", "weaknesses": "Needs randomised history; noisy", "data_needs": "Past campaigns with control groups"},
            {"name": "Profit-based selection", "papers": ["P4"], "how": "Evaluate and set cut-offs by expected campaign profit.",
             "strengths": "Ties the model to a business outcome", "weaknesses": "Depends on assumed costs and CLV", "data_needs": "Offer cost, contact cost, CLV"},
        ],
        "consensus": [
            {"claim": "Recency and frequency carry most of the signal about activity in non-contractual retail.", "papers": ["P1", "P2"], "confidence": "Likely"},
            {"claim": "Accuracy metrics alone pick the wrong model for retention decisions.", "papers": ["P3", "P4"], "confidence": "Likely"},
        ],
        "disagreements": [
            {"topic": "What to rank customers by", "sides": "[P1][P2][P4] rank by risk or value at risk. [P3] shows risk and responsiveness diverge and ranks by uplift."},
        ],
        "gaps": [
            {"gap": "None of these papers combines BTYD activity with uplift in one targeting score.",
             "opportunity": "Score = P(alive) × CLV × predicted uplift − offer cost, testable with one A/B campaign."},
            {"gap": "Loyalty-specific signals such as points balance and tier proximity are absent.",
             "opportunity": "Add points-to-next-reward as an uplift feature; it may explain who responds."},
        ],
        "reading_order": [
            {"paper": "P2", "why": "Fastest route to a working baseline"},
            {"paper": "P3", "why": "Changes what you optimise for"},
            {"paper": "P4", "why": "How to report results to the business"},
            {"paper": "P1", "why": "Theory behind P2, if you need to defend assumptions"},
        ],
    },
    "solutions": {
        "solutions": [
            sol("Control-group-first retention", "Hold out a random slice of every retention send so you can measure what offers really change.",
                ["P3"], ["Add a 10% random holdout to every retention campaign", "Log member, offer, treatment flag and 60-day outcome",
                         "After 2–3 campaigns, train the first uplift model"],
                "Creates the data every better method needs, at almost no cost.",
                ["Stakeholders resist holding customers back", "Value shows up only after a few campaigns"],
                "One rule in the campaign tool plus a results table",
                "Current campaigns have a smaller incremental effect than reported", "Lapse rate, treated vs holdout",
                "Effect measured with a confidence interval within 2 campaigns", "If holdouts are too small to show any signal, raise to 20% or pool campaigns",
                "S", "Certain"),
            sol("Value-at-risk × uplift scorer", "Rank members by the profit an offer is expected to create, not by how likely they are to leave.",
                ["P2", "P3", "P4"], ["Fit BG/NBD and Gamma-Gamma for P(alive) and 12-month CLV", "Train a T-learner uplift model on past campaigns with controls",
                                     "Score = P(alive) × CLV × uplift − offer cost", "Send only where expected profit is above zero"],
                "Fills the main gap from the synthesis; each piece is proven on its own.",
                ["Few past control groups means a weak uplift model", "CLV errors compound in the product"],
                "Notebook that scores all members, then one campaign split: top-risk vs top-score",
                "Targeting by score cuts lapse at lower cost than targeting by risk", "Incremental retained revenue per AED spent at 60 days",
                "At least 20% more incremental revenue per AED than risk targeting", "If neither arm beats control, the offer is the problem, not the targeting",
                "M", "Likely"),
            sol("Early-lapse nudges", "Watch each member's P(alive) and nudge softly when it drops below their own normal.",
                ["P1", "P2"], ["Recompute P(alive) nightly from the BTYD model", "Trigger a low-cost nudge below a per-member threshold", "Compare recovery against a holdout"],
                "Fast to ship, uses only purchase dates.",
                ["Threshold tuning can spam frequent buyers", "Still ranks by risk, which [P3] warns about"],
                "Nightly job writing a nudge list to the CRM",
                "Nudged members recover faster than holdout members", "Share purchasing within 30 days of the trigger",
                "+3 points vs holdout", "If lift sits only with members who would return anyway, switch to uplift ranking",
                "S", "Likely"),
        ],
        "recommendation": {"pick": "Control-group-first retention",
                           "why": "The scorer needs randomised history you probably don't have yet [P3]. Start holdouts this month, ship early-lapse nudges in parallel, and build the scorer once 2–3 campaigns of data exist. [Likely]"},
    },
}

# ---------------------------------------------------------------- 2. Ad incrementality
MEDIA = {
    "id": "demo-media", "demo": True,
    "name": "Is our paid media actually driving sales?",
    "problem": ("We spend across Meta, Google, TikTok and Snapchat. Every platform reports great ROAS, the totals add up "
                "to more sales than we actually made, and finance wants to cut 20% of budget. We need to know which "
                "spend is truly incremental."),
    "context": "E-commerce + app, AED 2M a quarter in paid media, GA4 and platform dashboards.",
    "constraints": "No data-science team; one analyst and the agency; decision needed next quarter.",
    "map": {
        "reframed_problem": ("How much of the sales credited to each channel would have happened without the ads, and how "
                             "should budget move across channels given diminishing returns?"),
        "why_hard": ("Ads target people who were already likely to buy, so attribution confuses correlation with cause, and "
                     "the true effect is small relative to the natural swings in sales."),
        "sub_questions": [
            "How reliable are observational methods compared with randomised experiments?",
            "How large must an experiment be to detect a realistic ad effect?",
            "How do we model carryover and saturation when moving budget between channels?",
            "How can we measure a one-off change, such as pausing a channel in one market?",
        ],
        "concepts": [
            {"term": "Incrementality", "meaning": "Sales that happened because of the ad and would not have happened otherwise."},
            {"term": "Lift test", "meaning": "A randomised experiment comparing exposed and held-out audiences."},
            {"term": "Media mix modelling (MMM)", "meaning": "A model of sales over time as a function of spend in each channel."},
            {"term": "Adstock", "meaning": "The carryover of an ad's effect into later weeks."},
            {"term": "Saturation", "meaning": "Each extra dirham buys less effect as spend rises."},
        ],
        "search_queries": [
            {"query": "advertising measurement field experiments observational methods", "purpose": "How wrong attribution can be"},
            {"query": "ghost ads online ad effectiveness", "purpose": "Leaner, cleaner lift tests"},
            {"query": "bayesian media mix model carryover saturation", "purpose": "Budget allocation across channels"},
            {"query": "causal impact bayesian structural time series", "purpose": "Measuring geo or market tests"},
        ],
        "landmark_papers": [
            sug("The Unfavorable Economics of Measuring the Returns to Advertising", "Lewis, Rao", "2015",
                "Shows why ad effects are hard to measure even with large experiments."),
            sug("A Comparison of Approaches to Advertising Measurement: Evidence from Big Field Experiments at Facebook",
                "Gordon, Zettelmeyer, Bhargava, Chapsky", "2019", "Tests observational methods against real experiments."),
            sug("Ghost Ads: Improving the Economics of Measuring Online Ad Effectiveness", "Johnson, Lewis, Nubbemeyer", "2017",
                "A leaner, more precise way to run lift tests."),
            sug("Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects", "Jin, Wang, Sun, Chan, Koehler", "2017",
                "The modern MMM template with adstock and saturation."),
            sug("Inferring causal impact using Bayesian structural time-series models", "Brodersen, Gallusser, Koehler, Remy, Scott", "2015",
                "Measures the effect of a one-off change against a modelled counterfactual."),
            sug("Challenges and Opportunities in Media Mix Modeling", "Chan, Perry", "2017",
                "Practical pitfalls of MMM from Google researchers.", "Likely"),
        ],
        "adjacent_fields": [
            {"field": "Econometrics", "why": "Difference-in-differences and synthetic control for geo tests."},
            {"field": "Experimental design", "why": "Power analysis for lift tests."},
        ],
    },
    "papers": [
        P(1, "The Unfavorable Economics of Measuring the Returns to Advertising", "Lewis, Rao", "2015",
          "The Quarterly Journal of Economics",
          "Ad effects are tiny compared with the natural noise in sales, so even huge experiments give wide answers.",
          ("Across many large online ad experiments at a major portal, individual purchase behaviour varied so much that "
           "plausible, profitable ad effects were hard to tell apart from zero. Measuring ROI precisely needs far more data "
           "than most advertisers assume."),
          "Analysis of 25 large field experiments run with US retailers and financial services firms.",
          [("Sales noise is so large relative to ad effects that experiments with millions of users can still give wide confidence intervals.", "Certain"),
           ("Very different ROIs, from loss-making to highly profitable, can be statistically hard to distinguish.", "Certain")],
          ["Results come from display advertising in the US, an older ad landscape", "Says what is hard, not which channel works"],
          ["Run a power calculation before every lift test; most are too small", "Treat a single platform ROAS figure as a wide range, not a number"],
          "Take last quarter's daily sales, compute its variance, and calculate how many users a test would need to detect a 2% lift.",
          5, "Sets realistic expectations for any measurement plan.",
          [("Statistical power", "The chance a test detects an effect that really exists.")]),
        P(2, "A Comparison of Approaches to Advertising Measurement: Evidence from Big Field Experiments at Facebook",
          "Gordon, Zettelmeyer, Bhargava, Chapsky", "2019", "Marketing Science",
          "Common observational methods often fail to recover the true lift that a randomised test finds.",
          ("The authors ran large randomised experiments on Facebook campaigns, then re-estimated the same effects using "
           "matching and regression methods on observational data. The observational answers were often far off, and "
           "frequently overstated the ad's effect."),
          "Fifteen large US advertising experiments on Facebook, compared with several observational estimators on the same data.",
          [("Observational methods frequently failed to match experimental lift estimates.", "Certain"),
           ("When they missed, they often overestimated the effect of the ads.", "Likely")],
          ["Facebook campaigns only", "Observational methods might do better with richer data"],
          ["Use platform-run lift studies as the ground truth for calibrating anything else", "Be most sceptical of attribution for retargeting"],
          "Request a conversion lift study for one Meta campaign and compare its result with the ROAS in Ads Manager.",
          5, "Direct evidence that attributed ROAS can mislead budget decisions.",
          [("Observational method", "Estimating an effect without random assignment."), ("RCT", "Randomised controlled trial.")]),
        P(3, "Ghost Ads: Improving the Economics of Measuring Online Ad Effectiveness", "Johnson, Lewis, Nubbemeyer", "2017",
          "Journal of Marketing Research",
          "Record when held-out users would have seen your ad, so lift tests compare like with like at no extra media cost.",
          ("Traditional tests show control users a charity ad, which costs money and adds noise. Ghost ads log the moments "
           "a control user would have been served the ad, letting you compare exposed users with genuinely comparable "
           "control users. That makes tests more efficient and more precise."),
          "Proposes the ghost-ad methodology and applies it to a large online retail campaign.",
          [("Ghost ads remove the cost of placebo ads and reduce noise compared with intent-to-treat comparisons.", "Certain")],
          ["Requires the ad platform to support it", "Still needs adequate sample size"],
          ["Prefer platform lift tools built on this idea over home-made holdouts", "Compare 'would-have-been-exposed' groups, not everyone"],
          "Check which of your four platforms offers ghost-ad style lift testing and what minimum budget each requires.",
          4, "Makes experiments affordable enough to run every quarter.",
          [("Ghost ad", "A logged, unserved impression for a control user."), ("Intent-to-treat", "Comparing everyone assigned, exposed or not.")]),
        P(4, "Bayesian Methods for Media Mix Modeling with Carryover and Shape Effects", "Jin, Wang, Sun, Chan, Koehler", "2017",
          "Google technical report",
          "A media mix model that captures how ad effects linger and saturate, with Bayesian priors to keep it sensible.",
          ("Sales are modelled as a function of each channel's spend, with an adstock curve for carryover and a Hill curve "
           "for saturation. Bayesian priors stabilise estimates when data is limited, and the fitted curves show where "
           "the next dirham does most good."),
          "Bayesian regression on weekly sales and spend, with adstock and Hill transforms; tested on simulated data.",
          [("Carryover and saturation shape budget recommendations materially.", "Certain"),
           ("Without lots of data or informative priors, parameters are poorly identified.", "Likely")],
          ["Needs 2+ years of weekly data with real spend variation", "Correlated channels are hard to separate"],
          ["Open-source versions exist: Google Meridian, Meta Robyn, PyMC-Marketing", "Use lift-test results as priors to calibrate"],
          "Fit PyMC-Marketing's MMM on 104 weeks of spend and sales, then compare its channel ranking with platform ROAS.",
          4, "The standard tool for cross-channel budget allocation.",
          [("Adstock", "Carryover of ad effect into later weeks."), ("Hill curve", "An S-shaped saturation curve.")]),
        P(5, "Inferring causal impact using Bayesian structural time-series models", "Brodersen, Gallusser, Koehler, Remy, Scott", "2015",
          "The Annals of Applied Statistics",
          "Estimate what sales would have been without a change, using markets that weren't changed, and measure the gap.",
          ("The model learns how a target series relates to control series before an intervention, then predicts the "
           "counterfactual after it. The difference between actual and predicted is the estimated effect, with uncertainty."),
          "Bayesian structural time-series with control series as regressors; released as the CausalImpact package.",
          [("Gives an effect estimate with credible intervals for a single intervention.", "Certain")],
          ["Control series must not be affected by the change", "Sensitive to how controls are chosen"],
          ["Pause one channel in one emirate or market and measure with CausalImpact against the others", "Use it for geo holdouts when platform lift tests aren't available"],
          "Pick a past promotion or channel pause and run CausalImpact on that market's daily sales against untouched markets.",
          4, "Measures channel pauses and geo tests without user-level data.",
          [("Counterfactual", "What would have happened without the change.")]),
    ],
    "synthesis": {
        "state_of_field": ("The evidence agrees that attributed ROAS is not a safe basis for cutting budget. Experiments are the "
                           "gold standard [P2] but are noisy and expensive [P1], made more efficient by ghost ads [P3]. MMM [P4] covers "
                           "all channels at once, and time-series methods [P5] measure geo tests."),
        "approaches": [
            {"name": "User-level lift tests", "papers": ["P2", "P3"], "how": "Randomly hold out users and compare outcomes.",
             "strengths": "Closest to true causal effect", "weaknesses": "One channel at a time; needs scale", "data_needs": "Platform lift tools, enough conversions"},
            {"name": "Media mix modelling", "papers": ["P4"], "how": "Regress weekly sales on transformed spend per channel.",
             "strengths": "All channels and offline at once", "weaknesses": "Correlational; needs spend variation", "data_needs": "2+ years weekly spend and sales"},
            {"name": "Geo / time-series experiments", "papers": ["P5"], "how": "Change spend in some markets and model the counterfactual.",
             "strengths": "No user tracking needed", "weaknesses": "Needs comparable markets", "data_needs": "Daily sales by market"},
        ],
        "consensus": [
            {"claim": "Platform-attributed ROAS is likely to overstate incremental effect.", "papers": ["P1", "P2"], "confidence": "Likely"},
            {"claim": "Experiments should anchor any model used for budget decisions.", "papers": ["P2", "P3", "P4"], "confidence": "Likely"},
        ],
        "disagreements": [
            {"topic": "Can you rely on models without experiments?", "sides": "[P4] argues priors and structure make MMM usable; [P2] shows observational methods often miss experimental truth."},
        ],
        "gaps": [
            {"gap": "Little guidance for smaller GCC budgets where lift tests may lack power.",
             "opportunity": "Pool tests across quarters and use them as priors in a single MMM."},
            {"gap": "None covers app-install and web sales in one measurement plan.",
             "opportunity": "A unified weekly dataset across app and web as the MMM target."},
        ],
        "reading_order": [
            {"paper": "P2", "why": "The case for testing, with real numbers"},
            {"paper": "P1", "why": "Why tests need to be big"},
            {"paper": "P4", "why": "How to allocate across channels"},
            {"paper": "P5", "why": "Quick geo tests you can run now"},
            {"paper": "P3", "why": "How platform lift tools work"},
        ],
    },
    "solutions": {
        "solutions": [
            sol("Lift-test ladder", "Run one platform lift test per month on the biggest channels and use the results as ground truth.",
                ["P2", "P3", "P1"], ["Size each test with a power calculation", "Start with the largest spend channel",
                                     "Record incremental cost per acquisition per test", "Compare with attributed ROAS to get a correction factor"],
                "Replaces arguments about attribution with measured lift.",
                ["Small channels may never reach power", "Platform-run tests are partly a black box"],
                "One Meta conversion lift study with a pre-registered success metric",
                "Attributed ROAS overstates incremental ROAS on our biggest channel", "Incremental CPA vs attributed CPA",
                "A correction factor with a confidence interval narrow enough to act on", "If the test is underpowered, move to a geo test instead",
                "S", "Likely"),
            sol("Geo holdout with CausalImpact", "Pause or halve one channel in one market for four weeks and measure the gap.",
                ["P5", "P1"], ["Pick a market with stable sales and good comparison markets", "Pause the channel for 4 weeks",
                               "Run CausalImpact against untouched markets", "Extrapolate budget impact carefully"],
                "Works for any channel, including ones without lift tools.",
                ["Markets differ in seasonality and events", "Short tests may miss carryover"],
                "One four-week pause plus a CausalImpact notebook",
                "Pausing the channel reduces sales by less than its attributed revenue", "Cumulative sales gap vs counterfactual",
                "Credible interval excludes the attributed revenue figure", "If the interval is too wide, extend the test or use more markets",
                "S", "Likely"),
            sol("Calibrated MMM for budget moves", "Fit an open-source MMM and calibrate it with lift-test results before moving money.",
                ["P4", "P2"], ["Assemble 104 weeks of spend and sales", "Fit PyMC-Marketing or Meridian MMM", "Set priors from lift tests",
                               "Simulate a 20% cut under different channel mixes"],
                "Answers finance's real question: where to cut with least damage.",
                ["Too little spend variation makes channels inseparable", "Needs analyst time each quarter"],
                "One MMM run with a budget simulator shared with finance",
                "Cutting the lowest-marginal-ROI channels loses less than 5% of sales", "Predicted vs actual sales after the reallocation",
                "Actual sales within the model's 80% interval", "If predictions miss badly, revert and gather more experimental priors",
                "M", "Guessing"),
        ],
        "recommendation": {"pick": "Lift-test ladder",
                           "why": "Finance needs a defensible answer this quarter, and experiments are the only evidence the papers trust [P2]. Run lift tests now, a geo pause in parallel [P5], and feed both into an MMM next quarter [P4]. [Likely]"},
    },
}

# ---------------------------------------------------------------- 3. Next-best offer
NBO = {
    "id": "demo-nbo", "demo": True,
    "name": "Next-best offer across app, email and WhatsApp",
    "problem": ("Every customer gets the same weekly promotion across app push, email and WhatsApp. Engagement is falling "
                "and unsubscribes are rising. We want to pick the right offer, channel and timing for each person."),
    "context": "Food and grocery delivery app, 1.2M monthly users, 40+ offer types.",
    "constraints": "Must run inside existing CRM; engineering can give 1 sprint per month.",
    "map": {
        "reframed_problem": ("How do we learn, online and safely, which offer works best for which customer, while still "
                             "exploring new offers, using mostly implicit signals like opens, clicks and orders?"),
        "why_hard": ("You only see the outcome of the offer you sent, not the ones you didn't, so learning and earning are in "
                     "tension, and feedback is sparse and implicit."),
        "sub_questions": [
            "How do we balance trying new offers with sending the best known one?",
            "How do we evaluate a new policy offline before going live?",
            "How do we learn preferences from clicks and orders rather than ratings?",
            "How should a large catalogue be narrowed before ranking?",
        ],
        "concepts": [
            {"term": "Contextual bandit", "meaning": "An algorithm that picks an action using context and learns from the reward it gets."},
            {"term": "Exploration vs exploitation", "meaning": "Trying uncertain options versus using the best known one."},
            {"term": "Thompson sampling", "meaning": "Picks options in proportion to the chance they are the best."},
            {"term": "Implicit feedback", "meaning": "Signals like clicks and purchases rather than explicit ratings."},
            {"term": "Off-policy evaluation", "meaning": "Estimating how a new policy would do using data logged by an old one."},
        ],
        "search_queries": [
            {"query": "contextual bandit personalized recommendation", "purpose": "Core method for offer selection"},
            {"query": "thompson sampling empirical evaluation", "purpose": "A simple, robust exploration rule"},
            {"query": "collaborative filtering implicit feedback", "purpose": "Learning from opens and orders"},
            {"query": "two stage recommender candidate generation ranking", "purpose": "Scaling to many offers"},
        ],
        "landmark_papers": [
            sug("A Contextual-Bandit Approach to Personalized News Article Recommendation", "Li, Chu, Langford, Schapire", "2010",
                "LinUCB plus a way to evaluate bandits offline."),
            sug("An Empirical Evaluation of Thompson Sampling", "Chapelle, Li", "2011", "Shows a simple exploration rule works very well."),
            sug("Collaborative Filtering for Implicit Feedback Datasets", "Hu, Koren, Volinsky", "2008", "How to learn from behaviour, not ratings."),
            sug("Deep Neural Networks for YouTube Recommendations", "Covington, Adams, Sargin", "2016", "The two-stage design used at scale."),
            sug("Matrix Factorization Techniques for Recommender Systems", "Koren, Bell, Volinsky", "2009", "Readable introduction to latent-factor models."),
        ],
        "adjacent_fields": [
            {"field": "Reinforcement learning", "why": "Longer-horizon effects such as fatigue and unsubscribes."},
            {"field": "Causal inference", "why": "Off-policy evaluation uses inverse propensity weighting."},
        ],
    },
    "papers": [
        P(1, "A Contextual-Bandit Approach to Personalized News Article Recommendation", "Li, Chu, Langford, Schapire", "2010",
          "WWW 2010",
          "Choose content per user with a bandit that balances trying new items and using known winners, and test it offline first.",
          ("The paper introduces LinUCB, which models each item's click-through rate as a function of user features and adds "
           "an uncertainty bonus to encourage exploration. It also shows how to evaluate a bandit offline by replaying "
           "randomly logged traffic, then validates on Yahoo! front-page data."),
          "LinUCB algorithm plus a replay method for unbiased offline evaluation on randomly logged data.",
          [("Contextual bandits beat context-free bandits on click-through in the Yahoo! experiments.", "Certain"),
           ("Replay on randomly logged data gives an unbiased offline estimate of a policy's performance.", "Certain")],
          ["Offline replay requires uniformly random logged data", "Optimises clicks, not longer-term value"],
          ["Log a small fully random slice of sends now so you can evaluate new policies offline later", "Start with a linear bandit on a few features"],
          "Send a random offer to 5% of users for two weeks, then replay a simple LinUCB policy on that log.",
          5, "The template for picking offers per user.",
          [("LinUCB", "A linear contextual bandit with an upper-confidence exploration bonus."), ("Replay evaluation", "Scoring a policy on logged random traffic.")]),
        P(2, "An Empirical Evaluation of Thompson Sampling", "Chapelle, Li", "2011", "NeurIPS 2011",
          "A decades-old, very simple exploration rule turns out to match or beat more complex methods in practice.",
          ("Thompson sampling keeps a probability distribution over each option's reward and picks options by sampling from "
           "those beliefs. In simulations and on display-ad and news data it performed as well as or better than popular "
           "alternatives, and coped well with delayed, batched feedback."),
          "Simulations plus experiments on display advertising and news recommendation data.",
          [("Thompson sampling is competitive with or better than UCB-style methods in these tests.", "Certain"),
           ("It is robust when feedback arrives late or in batches.", "Likely")],
          ["Results are empirical, not guarantees for every setting", "Needs a sensible prior"],
          ["Use Beta-Bernoulli Thompson sampling for offer choice per segment as a first version", "Batch updates daily; the method tolerates delay"],
          "Simulate 40 offers with made-up conversion rates and compare Thompson sampling with a fixed weekly promo over 8 weeks.",
          5, "The simplest robust algorithm for your first version.",
          [("Prior", "Your starting belief about each offer's conversion rate.")]),
        P(3, "Collaborative Filtering for Implicit Feedback Datasets", "Hu, Koren, Volinsky", "2008", "ICDM 2008",
          "Learn preferences from behaviour by treating actions as signals with varying confidence, not as ratings.",
          ("Instead of star ratings, the model uses whether a user interacted with an item as a preference and how much they "
           "interacted as confidence. An alternating least-squares method makes it scale to large datasets, demonstrated on "
           "TV viewing data."),
          "Weighted matrix factorisation with preference and confidence terms, solved with alternating least squares.",
          [("Separating preference from confidence improves recommendations from implicit data.", "Certain"),
           ("The method scales linearly with the amount of data.", "Likely")],
          ["Doesn't handle exploration or new offers", "Interactions don't capture negative feedback well"],
          ["Build user-offer embeddings from orders and clicks to feed a bandit as context", "Weight repeat orders higher than single clicks"],
          "Run the implicit library's ALS on 3 months of user-category orders and inspect the top recommendations for 20 users.",
          4, "How to turn order history into usable preferences.",
          [("ALS", "Alternating least squares, a fast way to fit matrix factorisation.")]),
        P(4, "Deep Neural Networks for YouTube Recommendations", "Covington, Adams, Sargin", "2016", "RecSys 2016",
          "Split recommendation into a fast candidate stage and a careful ranking stage, and optimise for the outcome you care about.",
          ("YouTube narrows millions of videos to hundreds with a candidate-generation network, then ranks those with a "
           "richer model. Ranking was trained to predict expected watch time rather than clicks, and live A/B tests were "
           "trusted over offline metrics."),
          "Two deep networks, candidate generation and ranking, trained on implicit feedback and evaluated with live A/B tests.",
          [("A two-stage design makes large-scale recommendation feasible.", "Certain"),
           ("Optimising for watch time rather than click-through gave better outcomes.", "Likely")],
          ["Built for massive scale and data", "Deep models are heavy for a CRM team"],
          ["Filter eligible offers with rules first, then rank the shortlist per user", "Optimise for orders or margin, not opens"],
          "Define a reward of 'order within 48 hours' and re-score last month's sends on it instead of open rate.",
          3, "Architecture idea is useful; the deep models are overkill to start.",
          [("Candidate generation", "Fast first pass that narrows the options.")]),
    ],
    "synthesis": {
        "state_of_field": ("Two families combine well. Bandits [P1][P2] decide what to send and keep learning; implicit-feedback "
                           "models [P3] turn order history into preference signals; and the two-stage design [P4] keeps "
                           "ranking manageable as offers grow."),
        "approaches": [
            {"name": "Contextual bandits", "papers": ["P1", "P2"], "how": "Pick an offer per user, observe reward, update.",
             "strengths": "Learns online; handles new offers", "weaknesses": "Optimises short-term reward", "data_needs": "Logged sends with outcomes"},
            {"name": "Implicit-feedback factorisation", "papers": ["P3"], "how": "Factorise user-item interactions weighted by confidence.",
             "strengths": "Rich preferences from behaviour", "weaknesses": "No exploration", "data_needs": "Orders and clicks per user"},
            {"name": "Two-stage ranking", "papers": ["P4"], "how": "Filter candidates, then rank with a richer model.",
             "strengths": "Scales to many offers", "weaknesses": "More engineering", "data_needs": "Large interaction logs"},
        ],
        "consensus": [
            {"claim": "Optimise for the business outcome, not clicks or opens.", "papers": ["P1", "P4"], "confidence": "Likely"},
            {"claim": "Some exploration is necessary to keep learning.", "papers": ["P1", "P2"], "confidence": "Certain"},
        ],
        "disagreements": [
            {"topic": "Simple vs complex exploration", "sides": "[P1] adds structured confidence bonuses (LinUCB); [P2] finds plain Thompson sampling matches it in practice."},
        ],
        "gaps": [
            {"gap": "None of these models channel choice or message fatigue.",
             "opportunity": "Treat offer × channel as the action, and subtract a penalty for unsubscribes from the reward."},
            {"gap": "WhatsApp-specific costs per message are absent.",
             "opportunity": "Include send cost in the reward so expensive channels must earn their place."},
        ],
        "reading_order": [
            {"paper": "P2", "why": "Simplest working algorithm"},
            {"paper": "P1", "why": "Adds context and offline evaluation"},
            {"paper": "P3", "why": "Better features from order history"},
            {"paper": "P4", "why": "Architecture when the catalogue grows"},
        ],
    },
    "solutions": {
        "solutions": [
            sol("Segment-level Thompson sampling", "Let each customer segment learn its best offer automatically each week.",
                ["P2"], ["Define 8–12 segments from RFM", "Run Beta-Bernoulli Thompson sampling per segment over 40 offers",
                         "Reward = order within 48 hours", "Update daily from CRM exports"],
                "Ships inside one sprint with a spreadsheet-level model.",
                ["Segments hide individual differences", "Order rewards are sparse for small segments"],
                "A daily script writing next week's offer per segment into the CRM",
                "Bandit-chosen offers beat the single weekly promo", "Orders per 1,000 sends, 4 weeks",
                "+10% orders per 1,000 sends vs control", "If no lift after 4 weeks, check offer diversity before blaming the algorithm",
                "S", "Likely"),
            sol("Offer × channel contextual bandit", "Pick both the offer and the channel per user, with a fatigue penalty.",
                ["P1", "P3"], ["Log a 5% random slice for offline evaluation", "Build user features plus ALS embeddings from orders",
                               "Train LinUCB over offer × channel actions", "Reward = margin − send cost − unsubscribe penalty"],
                "Directly attacks rising unsubscribes and channel cost, the gap in the papers.",
                ["More engineering than the CRM may allow", "Penalty weights are a judgement call"],
                "Offline replay showing the policy beats current sends on logged data",
                "A per-user policy raises margin per send while cutting unsubscribes", "Margin per send and unsubscribe rate",
                "+15% margin per send and −20% unsubscribes in replay", "If replay gains vanish live, shrink the action space",
                "M", "Guessing"),
            sol("Rules-then-rank shortlist", "Cut 40 offers to 5 eligible ones per user with rules, then rank by predicted order value.",
                ["P4", "P3"], ["Write eligibility rules (stock, location, recency)", "Score shortlisted offers with ALS affinity",
                               "Send the top offer on the user's most-engaged channel"],
                "Easy for marketers to understand and override.",
                ["No exploration, so new offers struggle", "Rules can go stale"],
                "Eligibility rules plus an affinity score column in the CRM",
                "Personal top offer beats the generic promo", "Orders per send",
                "+5% vs control", "If gains are small, add Thompson sampling on top of the shortlist",
                "S", "Likely"),
        ],
        "recommendation": {"pick": "Segment-level Thompson sampling",
                           "why": "It fits one sprint, and the evidence says simple Thompson sampling performs well [P2]. Log a random slice from day one so the per-user bandit [P1] can be evaluated offline before you build it. [Likely]"},
    },
}

# ---------------------------------------------------------------- 4. Reviews to decisions
REVIEWS = {
    "id": "demo-reviews", "demo": True,
    "name": "Turn customer reviews into product decisions",
    "problem": ("We collect around 30,000 app-store and product reviews a quarter in English and Arabic. The team reads "
                "a sample and reports a star average. We miss the specific issues that drive ratings and sales."),
    "context": "Consumer app and online store; reviews from App Store, Google Play and our site.",
    "constraints": "No labelled data; must be explainable to product managers; monthly report.",
    "map": {
        "reframed_problem": ("How do we automatically find what customers talk about, how they feel about each aspect, and "
                             "which issues actually move ratings and sales?"),
        "why_hard": ("Reviews mix several topics and sentiments in one text, language varies, and not every complaint "
                     "affects revenue equally."),
        "sub_questions": [
            "How do we extract product aspects and the sentiment about each one?",
            "How do we discover topics without labelled data?",
            "Do reviews actually affect sales, and which kind matter most?",
            "Which models handle short, informal, bilingual text?",
        ],
        "concepts": [
            {"term": "Aspect-based sentiment", "meaning": "Sentiment about specific features, such as delivery or price."},
            {"term": "Topic modelling", "meaning": "Grouping texts by theme without labels."},
            {"term": "Transformer embeddings", "meaning": "Numeric representations of text that capture meaning."},
            {"term": "Word of mouth", "meaning": "Customer-to-customer information that shapes demand."},
        ],
        "search_queries": [
            {"query": "mining and summarizing customer reviews", "purpose": "Aspect extraction foundations"},
            {"query": "BERTopic neural topic modeling", "purpose": "Modern topic discovery"},
            {"query": "online reviews effect on sales", "purpose": "Which reviews matter commercially"},
            {"query": "aspect based sentiment analysis transformers", "purpose": "Current methods"},
        ],
        "landmark_papers": [
            sug("Mining and Summarizing Customer Reviews", "Hu, Liu", "2004", "Founding paper on feature-level review summaries."),
            sug("The Effect of Word of Mouth on Sales: Online Book Reviews", "Chevalier, Mayzlin", "2006", "Shows reviews move sales, and bad ones move them more."),
            sug("BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", "Devlin, Chang, Lee, Toutanova", "2019",
                "The model family behind modern text classification."),
            sug("BERTopic: Neural topic modeling with a class-based TF-IDF procedure", "Grootendorst", "2022", "Practical topic discovery on embeddings."),
            sug("Thumbs up? Sentiment Classification using Machine Learning Techniques", "Pang, Lee, Vaithyanathan", "2002",
                "Early evidence that sentiment is harder than topic classification."),
        ],
        "adjacent_fields": [
            {"field": "Multilingual NLP", "why": "Arabic and code-switched reviews."},
            {"field": "Econometrics", "why": "Linking review changes to sales."},
        ],
    },
    "papers": [
        P(1, "Mining and Summarizing Customer Reviews", "Hu, Liu", "2004", "KDD 2004",
          "Summarise reviews by product feature: what people mention and whether they like it.",
          ("The method finds frequently mentioned product features, identifies opinion sentences about them, and decides "
           "whether each opinion is positive or negative. The output is a feature-by-feature summary rather than one average."),
          "Association mining for frequent features, opinion-word extraction, and WordNet-based orientation of adjectives.",
          [("Feature-level summaries are more useful than overall sentiment for product decisions.", "Likely"),
           ("Frequent noun phrases are a reasonable first proxy for product features.", "Certain")],
          ["Rule-based and English-only", "Misses implicit features and sarcasm"],
          ["Report sentiment per aspect (delivery, price, app speed), not one star average", "Start with a fixed list of 10 aspects your team cares about"],
          "Tag 200 reviews by aspect and sentiment by hand and see which three aspects dominate the negatives.",
          4, "Defines the output format your report should have.",
          [("Aspect", "A product feature customers talk about."), ("Opinion orientation", "Positive or negative stance.")]),
        P(2, "The Effect of Word of Mouth on Sales: Online Book Reviews", "Chevalier, Mayzlin", "2006", "Journal of Marketing Research",
          "Better reviews raise sales, and one-star reviews hurt more than five-star reviews help.",
          ("Comparing the same books on two retail sites, the authors find that an improvement in a book's reviews on one "
           "site raises its relative sales there. Negative reviews have a larger effect than positive ones."),
          "Difference-in-differences across Amazon and Barnes & Noble for the same titles.",
          [("Improvements in reviews lead to higher relative sales.", "Certain"),
           ("The impact of one-star reviews is greater than the impact of five-star reviews.", "Certain")],
          ["Books, an older market", "Effects in apps may differ"],
          ["Prioritise fixing issues behind 1–2 star reviews", "Track rating changes against sales by product"],
          "Plot weekly 1-star share against weekly sales for your top 20 products and look for leading signals.",
          4, "Tells you which reviews matter commercially.",
          [("Difference-in-differences", "Comparing changes across two groups to isolate an effect.")]),
        P(3, "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding", "Devlin, Chang, Lee, Toutanova", "2019",
          "NAACL 2019",
          "Pre-train a language model on huge text, then fine-tune it quickly for tasks like sentiment.",
          ("BERT learns word meaning from both left and right context by predicting masked words. Fine-tuned with a small "
           "labelled set, it set new results on many language benchmarks, including sentiment classification."),
          "Transformer encoder pre-trained with masked-language and next-sentence objectives, then fine-tuned per task.",
          [("Fine-tuned BERT improved the state of the art across a broad range of NLP benchmarks.", "Certain")],
          ["Needs labelled examples to fine-tune", "Base model is English; use multilingual or Arabic variants"],
          ["Use a multilingual or Arabic BERT variant for bilingual reviews", "A few hundred labelled reviews per aspect can go far"],
          "Fine-tune a small multilingual model on 500 labelled reviews and compare with a keyword baseline.",
          3, "Engine for accurate aspect sentiment once you have labels.",
          [("Fine-tuning", "Adapting a pre-trained model with a small labelled set.")]),
        P(4, "BERTopic: Neural topic modeling with a class-based TF-IDF procedure", "Grootendorst", "2022", "arXiv preprint",
          "Cluster review embeddings into topics and label each topic with its most distinctive words.",
          ("BERTopic embeds documents with a transformer, reduces dimensions, clusters similar documents, then uses a "
           "class-based TF-IDF to describe each cluster. It finds coherent topics without labels and can track them over time."),
          "Sentence embeddings, UMAP dimension reduction, HDBSCAN clustering, class-based TF-IDF topic words.",
          [("Produces coherent topics competitive with classic topic models.", "Likely"),
           ("Supports dynamic topics over time.", "Certain")],
          ["Short reviews can produce noisy clusters", "Topic labels need human naming"],
          ["Run monthly to spot new issues before they hit the star average", "Use multilingual embeddings for Arabic and English together"],
          "Run BERTopic on one quarter of reviews and name the top 15 topics with your product manager.",
          5, "The fastest way to discover issues without labels.",
          [("c-TF-IDF", "Words that best distinguish one topic from the others.")]),
    ],
    "synthesis": {
        "state_of_field": ("Discovery and measurement now work without much labelling: BERTopic [P4] finds themes, aspect "
                           "summaries [P1] give the right report shape, fine-tuned transformers [P3] sharpen sentiment, and the "
                           "sales evidence [P2] says negative reviews deserve the most attention."),
        "approaches": [
            {"name": "Aspect summaries", "papers": ["P1"], "how": "Extract features and opinion orientation per review.",
             "strengths": "Readable output for product teams", "weaknesses": "Rules break on informal text", "data_needs": "Raw reviews"},
            {"name": "Unsupervised topics", "papers": ["P4"], "how": "Embed, cluster and label reviews.",
             "strengths": "No labels; finds new issues", "weaknesses": "Needs human naming", "data_needs": "Thousands of reviews"},
            {"name": "Fine-tuned classifiers", "papers": ["P3"], "how": "Train a transformer on labelled aspect sentiment.",
             "strengths": "Most accurate", "weaknesses": "Needs labels", "data_needs": "A few hundred labels per aspect"},
        ],
        "consensus": [
            {"claim": "One overall sentiment score hides the actionable detail.", "papers": ["P1", "P4"], "confidence": "Likely"},
        ],
        "disagreements": [
            {"topic": "Labels or no labels", "sides": "[P3] relies on fine-tuning with labels; [P4] gets usable structure with none."},
        ],
        "gaps": [
            {"gap": "No paper here links discovered topics to revenue.",
             "opportunity": "Join monthly topic shares to sales by product and rank issues by revenue at risk, in the spirit of [P2]."},
            {"gap": "Arabic and mixed-language reviews are not covered.",
             "opportunity": "Test multilingual embeddings on a bilingual sample before scaling."},
        ],
        "reading_order": [
            {"paper": "P4", "why": "Gets you insights in a week"},
            {"paper": "P2", "why": "Tells you which issues to prioritise"},
            {"paper": "P1", "why": "Shapes the report"},
            {"paper": "P3", "why": "For accuracy later"},
        ],
    },
    "solutions": {
        "solutions": [
            sol("Monthly topic radar", "Automatically surface the top review topics each month and flag the fastest-growing negatives.",
                ["P4", "P2"], ["Embed reviews with a multilingual model", "Run BERTopic monthly", "Compare topic shares month on month",
                               "Flag rising topics in 1–2 star reviews"],
                "Replaces sampling with full coverage and spots issues early.",
                ["Topic names drift month to month", "Small topics can be noise"],
                "A notebook producing a one-page topic report",
                "Rising negative topics predict rating drops the following month", "Topic share vs next-month rating",
                "At least 3 issues flagged before they showed in the star average", "If flags don't lead ratings, switch to aspect sentiment",
                "S", "Likely"),
            sol("Aspect scorecard", "Score sentiment for 10 fixed aspects, such as delivery and price, every month.",
                ["P1", "P3"], ["Agree 10 aspects with product teams", "Label 500 reviews", "Fine-tune a multilingual classifier",
                               "Publish an aspect scorecard monthly"],
                "Gives PMs a stable, explainable KPI per aspect.",
                ["Labelling takes effort", "Fixed aspects miss new issues"],
                "Scorecard for 10 aspects using a fine-tuned model",
                "Aspect scores move before overall ratings", "Aspect sentiment vs rating trend",
                "Classifier F1 above 0.8 on held-out reviews", "If accuracy is low, merge aspects or label more data",
                "M", "Likely"),
            sol("Revenue-at-risk ranking", "Rank issues by the sales likely lost, not by how often they're mentioned.",
                ["P2", "P4"], ["Map topics to products", "Join to weekly sales", "Estimate the sales impact of rising negative topics",
                               "Rank the backlog by revenue at risk"],
                "Fills the gap between text analytics and money.",
                ["Correlation, not proven cause", "Needs clean product mapping"],
                "A ranked issue list with estimated revenue at risk",
                "Fixing top-ranked issues improves sales of affected products", "Sales of affected products after fixes",
                "Measurable recovery on at least 2 fixed issues", "If no sales link appears, keep ranking by rating impact",
                "M", "Guessing"),
        ],
        "recommendation": {"pick": "Monthly topic radar",
                           "why": "It needs no labels [P4] and can run this month. Weight its alerts toward one-star reviews, since those move sales most [P2], then add the aspect scorecard once you've labelled data. [Likely]"},
    },
}

# ---------------------------------------------------------------- 5. RAG support assistant
RAG = {
    "id": "demo-rag", "demo": True,
    "name": "A support assistant that answers from our policies",
    "problem": ("Our customer support team answers the same questions on returns, delivery and loyalty points all day. "
                "We want an AI assistant that answers from our policy documents, cites them, and never makes up a rule."),
    "context": "About 300 policy and FAQ pages, updated monthly, English and Arabic.",
    "constraints": "Must show sources; legal review required; pilot with the internal team first.",
    "map": {
        "reframed_problem": ("How do we retrieve the right policy passages for a question, get a language model to answer "
                             "only from them, and measure faithfulness before customers see it?"),
        "why_hard": ("Retrieval can miss the right passage, models can ignore or misuse context, and errors look confident."),
        "sub_questions": [
            "How should retrieval and generation be combined?",
            "Which retrieval method finds the right passage most reliably?",
            "How much context should we pass, and in what order?",
            "How do we measure faithfulness and relevance automatically?",
        ],
        "concepts": [
            {"term": "RAG", "meaning": "Retrieval-augmented generation: fetch relevant text, then generate an answer from it."},
            {"term": "Dense retrieval", "meaning": "Finding passages by meaning using embeddings, not keywords."},
            {"term": "BM25", "meaning": "A classic keyword-based ranking method."},
            {"term": "Faithfulness", "meaning": "Whether the answer is supported by the retrieved text."},
        ],
        "search_queries": [
            {"query": "retrieval augmented generation knowledge intensive", "purpose": "Founding RAG paper"},
            {"query": "dense passage retrieval open domain question answering", "purpose": "Retriever choice"},
            {"query": "lost in the middle long context language models", "purpose": "How to order context"},
            {"query": "RAG evaluation faithfulness metrics", "purpose": "Measuring quality before launch"},
        ],
        "landmark_papers": [
            sug("Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "Lewis, Perez, Piktus et al.", "2020", "Defines RAG."),
            sug("Dense Passage Retrieval for Open-Domain Question Answering", "Karpukhin, Oğuz, Min et al.", "2020", "Dense retriever that beat BM25."),
            sug("Lost in the Middle: How Language Models Use Long Contexts", "Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang", "2024",
                "Where relevant text sits in the prompt matters."),
            sug("RAGAS: Automated Evaluation of Retrieval Augmented Generation", "Es, James, Espinosa-Anke, Schockaert", "2024",
                "Reference-free metrics for RAG quality.", "Likely"),
            sug("Retrieval-Augmented Generation for Large Language Models: A Survey", "Gao, Xiong, Gao et al.", "2023", "Map of current RAG techniques."),
        ],
        "adjacent_fields": [
            {"field": "Information retrieval", "why": "Hybrid keyword + dense search and re-ranking."},
            {"field": "Evaluation and QA", "why": "Golden question sets and human review loops."},
        ],
    },
    "papers": [
        P(1, "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks", "Lewis, Perez, Piktus et al.", "2020", "NeurIPS 2020",
          "Let a language model look things up in a document index before answering, instead of relying only on what it memorised.",
          ("RAG pairs a neural retriever over a document index with a text generator. The generator conditions on retrieved "
           "passages, which improved results on knowledge-heavy question answering and made answers easier to update by "
           "changing the index rather than the model."),
          "DPR retriever over a Wikipedia index combined with a BART generator, trained end to end.",
          [("Retrieval improved performance on open-domain question answering benchmarks.", "Certain"),
           ("Knowledge can be updated by swapping the index without retraining.", "Certain")],
          ["Uses Wikipedia, not company documents", "Older generator model"],
          ["Keep policies in an index you can update monthly; never rely on the model's memory for rules", "Return the passages used, so answers can cite them"],
          "Index 30 policy pages, ask 20 real support questions, and check how often the right page is retrieved in the top 3.",
          5, "The base architecture for your assistant.",
          [("Index", "A searchable store of document chunks."), ("Generator", "The model that writes the answer.")]),
        P(2, "Dense Passage Retrieval for Open-Domain Question Answering", "Karpukhin, Oğuz, Min et al.", "2020", "EMNLP 2020",
          "Retrieve passages by meaning with two encoders, one for questions and one for passages.",
          ("A dual-encoder model trained on question-passage pairs retrieved relevant passages far better than BM25 keyword "
           "search on several QA datasets, which in turn improved end-to-end answer accuracy."),
          "Dual BERT encoders trained with in-batch negatives; nearest-neighbour search over passage embeddings.",
          [("Dense retrieval clearly outperformed BM25 on top-20 passage retrieval accuracy in their benchmarks.", "Certain")],
          ["Keyword search still wins on exact terms like SKU codes", "Needs good embeddings for Arabic"],
          ["Use hybrid search: embeddings plus keyword matching for policy codes", "Measure top-k retrieval accuracy on your own questions"],
          "Compare BM25 and an embedding model on 50 real questions; count how often the right passage is in the top 5.",
          4, "Decides how your assistant finds the right policy.",
          [("Dual encoder", "Separate models that embed questions and passages into the same space.")]),
        P(3, "Lost in the Middle: How Language Models Use Long Contexts", "Liu, Lin, Hewitt, Paranjape, Bevilacqua, Petroni, Liang", "2024",
          "Transactions of the ACL",
          "Models use information at the start or end of a long prompt better than information buried in the middle.",
          ("In multi-document QA and key-value retrieval tests, accuracy was highest when the relevant information appeared at "
           "the beginning or end of the context and dropped when it sat in the middle, even for long-context models."),
          "Controlled experiments varying the position of relevant documents in the input across several language models.",
          [("Performance follows a U-shape: best at the start or end of the context, worse in the middle.", "Certain"),
           ("More retrieved documents is not always better.", "Likely")],
          ["Tested on specific benchmarks and models", "Newer models may be less affected"],
          ["Send fewer, better passages, with the best one first", "Re-rank retrieved chunks before building the prompt"],
          "Ask 20 questions with the right passage placed first, then in the middle of 10 passages, and compare accuracy.",
          4, "Tells you how to build the prompt.",
          [("Context window", "The amount of text a model reads at once.")]),
        P(4, "RAGAS: Automated Evaluation of Retrieval Augmented Generation", "Es, James, Espinosa-Anke, Schockaert", "2024",
          "EACL 2024 (system demonstrations)",
          "Score RAG answers for faithfulness, answer relevance and context relevance without human-written reference answers.",
          ("RAGAS uses a language model to judge whether answer statements are supported by the retrieved context, whether "
           "the answer addresses the question, and whether the retrieved context is focused. This makes regular evaluation "
           "fast enough to run on every change."),
          "LLM-based metrics for faithfulness, answer relevance and context relevance, compared with human judgements.",
          [("Automated metrics broadly agree with human judgements of faithfulness.", "Likely")],
          ["An LLM judging an LLM can share its blind spots", "Doesn't replace legal review"],
          ["Build a golden set of 100 real questions and run faithfulness scoring on every release", "Block launch below an agreed faithfulness score"],
          "Score 30 assistant answers with RAGAS faithfulness and compare with your support lead's judgement.",
          4, "Makes 'never make up a rule' measurable.",
          [("Faithfulness", "Share of answer claims supported by the retrieved text.")], knowledge="Likely"),
    ],
    "synthesis": {
        "state_of_field": ("The recipe is settled: retrieve [P1][P2], keep context short and well ordered [P3], and measure "
                           "faithfulness continuously [P4]. Most failures come from retrieval misses and prompt construction, "
                           "not the model."),
        "approaches": [
            {"name": "Retrieve-then-generate", "papers": ["P1"], "how": "Fetch passages and condition the answer on them.",
             "strengths": "Updatable, citable", "weaknesses": "Depends on retrieval quality", "data_needs": "Clean policy documents"},
            {"name": "Dense / hybrid retrieval", "papers": ["P2"], "how": "Embed questions and passages and match by meaning.",
             "strengths": "Handles paraphrased questions", "weaknesses": "Misses exact codes alone", "data_needs": "Embeddings for both languages"},
            {"name": "Context engineering", "papers": ["P3"], "how": "Re-rank and order a small set of passages.",
             "strengths": "Quick accuracy gains", "weaknesses": "Model-specific", "data_needs": "Test questions"},
            {"name": "Automated evaluation", "papers": ["P4"], "how": "LLM-judged faithfulness and relevance.",
             "strengths": "Runs on every change", "weaknesses": "Judge can be wrong", "data_needs": "Golden question set"},
        ],
        "consensus": [
            {"claim": "Answer quality is bounded by retrieval quality.", "papers": ["P1", "P2"], "confidence": "Likely"},
            {"claim": "Less, better-ordered context beats stuffing the prompt.", "papers": ["P3"], "confidence": "Likely"},
        ],
        "disagreements": [
            {"topic": "Dense or keyword retrieval", "sides": "[P2] shows dense beats BM25 on open QA; practitioners still pair it with keywords for exact terms."},
        ],
        "gaps": [
            {"gap": "None of the papers handles policies that change monthly or conflict across versions.",
             "opportunity": "Version-stamp every chunk and retrieve only the current version."},
            {"gap": "Refusal behaviour, saying 'I don't know', is not evaluated.",
             "opportunity": "Add unanswerable questions to the golden set and score correct refusals."},
        ],
        "reading_order": [
            {"paper": "P1", "why": "The architecture"},
            {"paper": "P4", "why": "How you'll prove it's safe"},
            {"paper": "P2", "why": "Retriever choice"},
            {"paper": "P3", "why": "Prompt construction"},
        ],
    },
    "solutions": {
        "solutions": [
            sol("Cited answers with refusal", "Answer only from retrieved policy passages, cite them, and refuse when nothing matches.",
                ["P1", "P2", "P3"], ["Chunk and version-stamp 300 pages", "Hybrid search with re-ranking, top 3 passages, best first",
                                     "Prompt: answer only from passages, cite each, else refuse", "Show citations to agents"],
                "Meets the 'never make up a rule' requirement by design.",
                ["Refuses too often if retrieval is weak", "Arabic retrieval needs testing"],
                "Internal Streamlit app for 10 support agents",
                "Agents accept most answers without editing", "Share of answers accepted as-is",
                "70% accepted, 0 policy errors in a 2-week pilot", "If errors appear, tighten refusal and review retrieval misses",
                "M", "Likely"),
            sol("Golden-set release gate", "Never ship a change without passing a 100-question faithfulness test.",
                ["P4"], ["Collect 100 real questions, including 15 unanswerable", "Write expected sources with the support lead",
                         "Run RAGAS faithfulness and retrieval hit rate on every change", "Block releases below thresholds"],
                "Turns legal's worry into a measurable gate.",
                ["Golden set must be kept current", "LLM judge may miss subtle errors"],
                "A test script plus a results table per release",
                "Automated scores track human review", "Agreement between RAGAS and human ratings",
                "80% agreement on faithfulness labels", "If agreement is low, use human review for the gate",
                "S", "Likely"),
            sol("Agent-assist before customer-facing", "Draft replies inside the agent's tool first, then go customer-facing once metrics hold.",
                ["P1", "P4"], ["Integrate drafts into the support tool", "Log edits agents make", "Feed edits back into the golden set",
                               "Open to customers for top 20 question types"],
                "Gets value quickly with a human in the loop.",
                ["Agents may over-trust drafts", "Slower path to automation"],
                "Draft button in the support tool for the top 20 intents",
                "Drafts cut handling time without errors", "Average handling time and error rate",
                "−25% handling time, no rise in errors", "If time doesn't drop, retrieval or tone needs work",
                "M", "Likely"),
        ],
        "recommendation": {"pick": "Golden-set release gate",
                           "why": "Build the 100-question test first, since it is what lets legal sign off [P4], then pilot cited answers with refusal internally [P1][P3]. [Likely]"},
    },
}

DEMO_PROJECTS = [LOYALTY, MEDIA, NBO, REVIEWS, RAG]
