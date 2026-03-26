export default {
    en: {
        eyebrow: "Polis export mirror",
        nav: {
            consensus: "Consensus",
            statements: "Statements",
            participants: "Participants",
            method: "Method",
        },
        stats: {
            participants: "Participants",
            votes: "Votes",
            statements: "Statements",
            clusters: "Clusters",
        },
        consensus: {
            badge: "Living consensus",
            title: "Current bridge statement",
            description:
                "This lead statement is derived from overall support and the weakest support across the discovered Polis clusters.",
            support: "Overall support",
            bridge: "Weakest-cluster support",
            strongestGroup: "Strongest in",
            weakestGroup: "Weakest in",
            timeline: "Consensus trail",
            timelineDescription:
                "Cumulative checkpoints where the leading statement changed.",
            statementDynamics: "Statement dynamics",
            opinionDynamics: "Opinion dynamics",
            sourceWindow: "Activity window",
            source: "Original Polis conversation",
        },
        statements: {
            kicker: "Statement map",
            title: "Ranked public statements",
            description:
                "Each dot is a Polis statement. Proximity comes from similar voting patterns, while size and colour reflect the derived bridge score.",
            cardMeta: "support",
            bridgeMeta: "bridge floor",
            detailTitle: "Selected statement",
            detailSupport: "Support",
            detailDisagreement: "Disagreement",
            detailVotes: "Votes",
            groupSupport: "Cluster support",
            created: "Posted",
        },
        participants: {
            kicker: "Participant map",
            title: "Anonymous voting blocs and participants",
            description:
                "Participants are coloured by Polis cluster when available. The map is a lightweight vote-pattern projection, not a semantic embedding.",
            ribbonTitle: "Cluster balance",
            detailTitle: "Selected participant",
            authorTag: "Comment author",
            agrees: "Agreed with",
            disagrees: "Pushed back on",
            voteStrip: "Vote strip",
            votes: "Votes cast",
        },
        method: {
            title: "Method and limits",
            description:
                "This page aims for a Habermolt-like reading experience, but it stays honest about what Polis exports can and cannot provide.",
            sources: "CSV sources",
            limitations: "What this reconstruction does",
            note: "No hidden APIs were used. Everything on the page is derived from the five export files above.",
        },
        dynamics: {
            converging: {
                label: "Converging",
                icon: "↗",
                description:
                    "Leadership is stabilising around one bridge statement.",
            },
            contested: {
                label: "Contested",
                icon: "⇄",
                description:
                    "Top statements are close enough that the lead still feels fragile.",
            },
            settled: {
                label: "Settled",
                icon: "●",
                description:
                    "One statement has held the lead for a sustained stretch.",
            },
            volatile: {
                label: "Volatile",
                icon: "↯",
                description:
                    "Leadership changed repeatedly as more votes arrived.",
            },
            aligned: {
                label: "Aligned",
                icon: "◎",
                description:
                    "Most participants behave like one broad voting bloc.",
            },
            polarized: {
                label: "Polarized",
                icon: "⊖",
                description: "Two sizable blocs pull in different directions.",
            },
            lopsided: {
                label: "Lopsided",
                icon: "◐",
                description:
                    "One bloc dominates while a much smaller bloc resists.",
            },
            fragmented: {
                label: "Fragmented",
                icon: "◇",
                description:
                    "Several blocs coexist without one dominant centre.",
            },
            diverse: {
                label: "Diverse",
                icon: "✦",
                description:
                    "Voting patterns spread out without clean cluster boundaries.",
            },
        },
        status: {
            agree: "Agree",
            pass: "Pass",
            disagree: "Disagree",
        },
        errorTitle: "Polis export unavailable",
        errorDescription:
            "The page template is ready, but the build could not fetch the Polis CSV exports at this moment.",
    },
    tw: {
        eyebrow: "Polis 匯出鏡像",
        nav: {
            consensus: "共識",
            statements: "陳述",
            participants: "參與者",
            method: "方法",
        },
        stats: {
            participants: "參與者",
            votes: "投票",
            statements: "陳述",
            clusters: "分群",
        },
        consensus: {
            badge: "當前共識",
            title: "目前最能搭橋的陳述",
            description:
                "這條領先陳述是依據整體支持度，以及各 Polis 分群中最弱的一段支持度推導出來的。",
            support: "整體支持",
            bridge: "最弱分群支持",
            strongestGroup: "最支持於",
            weakestGroup: "最薄弱於",
            timeline: "共識軌跡",
            timelineDescription:
                "在累積投票檢查點上，領先陳述曾經發生變化的時刻。",
            statementDynamics: "陳述動態",
            opinionDynamics: "意見動態",
            sourceWindow: "活動期間",
            source: "原始 Polis 對話",
        },
        statements: {
            kicker: "陳述地圖",
            title: "排序後的公共陳述",
            description:
                "每個點都是一條 Polis 陳述。點與點的接近程度來自相似的投票模式；大小與顏色則反映推導出的搭橋分數。",
            cardMeta: "支持",
            bridgeMeta: "搭橋底線",
            detailTitle: "選取的陳述",
            detailSupport: "支持",
            detailDisagreement: "反對",
            detailVotes: "票數",
            groupSupport: "各群支持",
            created: "發佈時間",
        },
        participants: {
            kicker: "參與者地圖",
            title: "匿名投票群塊與參與者",
            description:
                "若 Polis 有提供分群，參與者就以該分群上色。這張地圖是輕量級的投票模式投影，不是語意嵌入。",
            ribbonTitle: "分群分布",
            detailTitle: "選取的參與者",
            authorTag: "留言作者",
            agrees: "同意了",
            disagrees: "提出異議",
            voteStrip: "投票帶",
            votes: "已投票數",
        },
        method: {
            title: "方法與限制",
            description:
                "這一頁試著重現 Habermolt 的閱讀體驗，但也清楚說明 Polis 匯出資料能提供與無法提供的是什麼。",
            sources: "CSV 來源",
            limitations: "這個重建做了什麼",
            note: "本頁沒有使用隱藏 API。所有內容都由上面的五個匯出檔推導而來。",
        },
        dynamics: {
            converging: {
                label: "收斂中",
                icon: "↗",
                description: "領先地位正逐漸穩定在單一搭橋陳述上。",
            },
            contested: {
                label: "競逐中",
                icon: "⇄",
                description: "前幾名陳述仍然很接近，領先地位還不穩固。",
            },
            settled: {
                label: "已穩定",
                icon: "●",
                description: "有一條陳述在相當一段時間裡持續領先。",
            },
            volatile: {
                label: "波動中",
                icon: "↯",
                description: "隨著更多投票進來，領先陳述反覆更替。",
            },
            aligned: {
                label: "整體一致",
                icon: "◎",
                description: "大多數參與者的投票行為像是一個寬鬆的大群體。",
            },
            polarized: {
                label: "兩極化",
                icon: "⊖",
                description: "兩個不小的群體朝不同方向拉扯。",
            },
            lopsided: {
                label: "失衡",
                icon: "◐",
                description: "一個群體占了上風，而較小的群體持續抗拒。",
            },
            fragmented: {
                label: "碎片化",
                icon: "◇",
                description: "好幾個群體並存，沒有單一中心。",
            },
            diverse: {
                label: "多樣分散",
                icon: "✦",
                description: "投票模式分散開來，沒有明顯的分群邊界。",
            },
        },
        status: {
            agree: "同意",
            pass: "略過",
            disagree: "反對",
        },
        errorTitle: "目前無法取得 Polis 匯出",
        errorDescription:
            "頁面模板已經準備好，但這次建置時暫時無法抓取 Polis 的 CSV 匯出。",
    },
};
