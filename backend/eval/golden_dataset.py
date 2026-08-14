"""
Golden Evaluation Dataset for AlphaRead RAG Pipeline Benchmarking (~25 Q&A Pairs).
Contains ground truth questions, reference answers, and expected SEC 10-K filing tickers.
"""

GOLDEN_DATASET = [
    {
        "question": "What were Microsoft's major revenue drivers in Item 7 MD&A?",
        "ground_truth": "Microsoft's revenue growth was primarily driven by Intelligent Cloud services, Azure cloud infrastructure growth, server products, and Office 365 commercial subscriptions.",
        "ticker": "MSFT",
        "section": "Item 7"
    },
    {
        "question": "What are the primary risk factors identified for Nvidia in Item 1A?",
        "ground_truth": "Nvidia's primary risks include semiconductor supply chain constraints, intense competition in graphics and AI hardware, macroeconomic fluctuations, international trade regulations, and customer concentration.",
        "ticker": "NVDA",
        "section": "Item 1A"
    },
    {
        "question": "How does Apple describe its business operations and product ecosystem in Item 1?",
        "ground_truth": "Apple designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories, supported by a services ecosystem including App Store, Apple Music, iCloud, and Apple Pay.",
        "ticker": "AAPL",
        "section": "Item 1"
    },
    {
        "question": "What key competition risks are listed for Tesla in Item 1A?",
        "ground_truth": "Tesla faces competition from established automotive OEMs and new EV startups, risks regarding battery raw material prices, manufacturing scaling, autonomous software regulation, and lithium supply chains.",
        "ticker": "TSLA",
        "section": "Item 1A"
    },
    {
        "question": "What are Amazon's primary operating segments discussed in Item 7?",
        "ground_truth": "Amazon operates three main segments: North America, International, and Amazon Web Services (AWS), with AWS driving a significant portion of consolidated operating income.",
        "ticker": "AMZN",
        "section": "Item 7"
    },
    {
        "question": "What risk factors does Alphabet (Google) highlight regarding AI and regulatory compliance?",
        "ground_truth": "Alphabet highlights risks related to rapid technological change in artificial intelligence, antitrust investigations, global data privacy regulations (GDPR/CCPA), and ad revenue dependence.",
        "ticker": "GOOGL",
        "section": "Item 1A"
    },
    {
        "question": "What are Microsoft's main risk factors regarding cybersecurity and data privacy in Item 1A?",
        "ground_truth": "Microsoft identifies risks from sophisticated cyberattacks, data security breaches, platform outages, and evolving compliance obligations across international data jurisdictions.",
        "ticker": "MSFT",
        "section": "Item 1A"
    },
    {
        "question": "What operational metrics and cloud growth highlights are detailed in Microsoft's MD&A?",
        "ground_truth": "Microsoft highlighted expanded operating margins, strong cash flow from operations, increased enterprise cloud commitments, and capital expenditures dedicated to AI data center buildouts.",
        "ticker": "MSFT",
        "section": "Item 7"
    },
    {
        "question": "What supply chain dependencies does Apple report in Item 1A?",
        "ground_truth": "Apple relies on single-source or limited-source suppliers for custom components, semiconductor foundries primarily in Asia, and outsourced assembly partners.",
        "ticker": "AAPL",
        "section": "Item 1A"
    },
    {
        "question": "What are Nvidia's core business segments in Item 1?",
        "ground_truth": "Nvidia operates in Compute & Networking (Data Center AI platforms, Networking) and Graphics (GeForce GPUs, Quadro/NVIDIA RTX workstation graphics).",
        "ticker": "NVDA",
        "section": "Item 1"
    },
    {
        "question": "What financial liquidity disclosures are made by Tesla in Item 7?",
        "ground_truth": "Tesla maintains liquidity through cash and cash equivalents, operating cash flow, customer deposits, and credit facilities to fund gigafactory expansions and R&D.",
        "ticker": "TSLA",
        "section": "Item 7"
    },
    {
        "question": "What regulatory and legal risks does Amazon face in Item 1A?",
        "ground_truth": "Amazon faces legal scrutinies regarding marketplace seller practices, labor regulation, environmental disclosures, antitrust lawsuits, and international tax laws.",
        "ticker": "AMZN",
        "section": "Item 1A"
    },
    {
        "question": "How does Alphabet summarize its R&D investment strategy in Item 7?",
        "ground_truth": "Alphabet invests heavily in research and development for deep learning, search algorithms, cloud infrastructure, quantum computing, and consumer hardware innovations.",
        "ticker": "GOOGL",
        "section": "Item 7"
    },
    {
        "question": "What credit and currency risk factors are discussed in Microsoft's filing?",
        "ground_truth": "Microsoft manages foreign currency exchange rate volatility through hedging contracts and monitors commercial counterparty credit risks across global accounts receivable.",
        "ticker": "MSFT",
        "section": "Item 1A"
    },
    {
        "question": "What key disclosures are made regarding Apple Services growth in Item 7?",
        "ground_truth": "Apple Services experienced margin expansion driven by higher transaction volumes, paid digital subscriptions, licensing fees, and cloud storage monetization.",
        "ticker": "AAPL",
        "section": "Item 7"
    },
    {
        "question": "What hardware component shortages affect Nvidia's production in Item 1A?",
        "ground_truth": "Nvidia relies on advanced packaging technologies (CoWoS) and semiconductor fabrication foundries (TSMC), making it vulnerable to wafer capacity bottlenecks.",
        "ticker": "NVDA",
        "section": "Item 1A"
    },
    {
        "question": "How does Tesla discuss research & development spending trends in Item 7?",
        "ground_truth": "Tesla R&D spending focuses on Full Self-Driving (FSD) neural network training, next-gen vehicle platform engineering, custom AI silicon, and battery cell manufacturing.",
        "ticker": "TSLA",
        "section": "Item 7"
    },
    {
        "question": "What international revenue risks does Amazon cite in Item 1A?",
        "ground_truth": "Amazon cites foreign exchange rate headwinds, international regulatory compliance, tariffs, geopolitical conflicts, and local e-commerce competition.",
        "ticker": "AMZN",
        "section": "Item 1A"
    },
    {
        "question": "What risk disclosures are made regarding Google Search advertising in Item 1A?",
        "ground_truth": "Alphabet's advertising revenues could be impacted by changes in consumer online behavior, ad-blocking software, mobile operating system privacy policies, and competitive search platforms.",
        "ticker": "GOOGL",
        "section": "Item 1A"
    },
    {
        "question": "What capital expenditure plans does Microsoft outline for cloud infrastructure?",
        "ground_truth": "Microsoft outlines significant capital expenditures dedicated to leasing and building data centers, acquiring server hardware, GPUs, and network equipment to support cloud AI workloads.",
        "ticker": "MSFT",
        "section": "Item 7"
    },
    {
        "question": "What intellectual property risks are highlighted by Apple in Item 1A?",
        "ground_truth": "Apple is subject to intellectual property litigation, patent infringement claims from non-practicing entities, and risks related to protecting proprietary designs globally.",
        "ticker": "AAPL",
        "section": "Item 1A"
    },
    {
        "question": "What is Nvidia's strategy regarding Data Center AI market expansion in Item 1?",
        "ground_truth": "Nvidia accelerates data center adoption by integrating accelerated computing hardware (HGX, DGX), high-speed networking (Mellanox InfiniBand), and enterprise AI software stacks (NVIDIA AI Enterprise).",
        "ticker": "NVDA",
        "section": "Item 1"
    },
    {
        "question": "What risks regarding raw material costs does Tesla detail in Item 1A?",
        "ground_truth": "Tesla details cost exposure to volatile prices for lithium, nickel, cobalt, aluminum, and steel, which directly impact battery pack and vehicle manufacturing margins.",
        "ticker": "TSLA",
        "section": "Item 1A"
    },
    {
        "question": "How does Amazon Web Services (AWS) contribute to Amazon's profitability in Item 7?",
        "ground_truth": "AWS generates high operating margins due to scale, cloud migration demand, and enterprise infrastructure services, serving as a primary cash driver for Amazon's business.",
        "ticker": "AMZN",
        "section": "Item 7"
    },
    {
        "question": "What cybersecurity and network infrastructure risks are noted by Alphabet in Item 1A?",
        "ground_truth": "Alphabet cites risks associated with service disruptions, distributed denial-of-service (DDoS) attacks, hardware failures in data centers, and security threats to user data.",
        "ticker": "GOOGL",
        "section": "Item 1A"
    }
]
