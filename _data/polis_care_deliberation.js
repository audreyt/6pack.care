const EXPORT_ID = "r2jstrdchy3udbrf8arjx";
const BASE_URL = `https://polis.comhairle.scot/api/v3/reportExport/${EXPORT_ID}`;
const EN_DATE = new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    month: "short",
    year: "numeric",
});
const TW_DATE = new Intl.DateTimeFormat("zh-Hant-TW", {
    day: "numeric",
    month: "long",
    year: "numeric",
});
const EN_TIME = new Intl.DateTimeFormat("en-GB", {
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    month: "short",
});
const TW_TIME = new Intl.DateTimeFormat("zh-Hant-TW", {
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
    month: "long",
});
const CLUSTER_STYLES = [
    {
        code: "A",
        color: "#2a7f8a",
        soft: "#e6f1f2",
    },
    {
        code: "B",
        color: "#c4614a",
        soft: "#f8e9e4",
    },
    {
        code: "C",
        color: "#b8860b",
        soft: "#f6efdb",
    },
];
const UNCLUSTERED_STYLE = {
    code: "U",
    color: "#6c7a89",
    soft: "#ebeff2",
};

function toInt(value) {
    const parsed = Number.parseInt(value ?? "", 10);
    return Number.isFinite(parsed) ? parsed : 0;
}

function normalizeText(value) {
    return String(value ?? "")
        .replace(/\s+/g, " ")
        .trim();
}

function percent(value) {
    return Math.round((value || 0) * 100);
}

function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
}

function parseCsvRows(text) {
    const rows = [];
    let row = [];
    let field = "";
    let inQuotes = false;

    for (let index = 0; index < text.length; index += 1) {
        const char = text[index];

        if (inQuotes) {
            if (char === '"') {
                if (text[index + 1] === '"') {
                    field += '"';
                    index += 1;
                } else {
                    inQuotes = false;
                }
            } else {
                field += char;
            }
            continue;
        }

        if (char === '"') {
            inQuotes = true;
        } else if (char === ",") {
            row.push(field);
            field = "";
        } else if (char === "\n") {
            row.push(field);
            rows.push(row);
            row = [];
            field = "";
        } else if (char !== "\r") {
            field += char;
        }
    }

    if (field.length > 0 || row.length > 0) {
        row.push(field);
        rows.push(row);
    }

    return rows.filter((candidate) => candidate.some((cell) => cell !== ""));
}

function parseCsvObjects(text) {
    const [headers = [], ...rows] = parseCsvRows(text);
    return rows.map((row) =>
        Object.fromEntries(
            headers.map((header, index) => [header, row[index] ?? ""])
        )
    );
}

function parseSummary(text) {
    return Object.fromEntries(parseCsvRows(text));
}

function formatDatePair(value) {
    const date = value instanceof Date ? value : new Date(value);
    return {
        en: EN_DATE.format(date),
        tw: TW_DATE.format(date),
    };
}

function formatDateTimePair(value) {
    const date = value instanceof Date ? value : new Date(value);
    return {
        en: EN_TIME.format(date),
        tw: TW_TIME.format(date),
    };
}

function mixColors(hexA, hexB, ratio) {
    const weight = clamp(ratio, 0, 1);
    const parse = (hex) => [
        Number.parseInt(hex.slice(1, 3), 16),
        Number.parseInt(hex.slice(3, 5), 16),
        Number.parseInt(hex.slice(5, 7), 16),
    ];
    const [aR, aG, aB] = parse(hexA);
    const [bR, bG, bB] = parse(hexB);
    const toHex = (value) => value.toString(16).padStart(2, "0");
    const red = Math.round(aR + (bR - aR) * weight);
    const green = Math.round(aG + (bG - aG) * weight);
    const blue = Math.round(aB + (bB - aB) * weight);
    return `#${toHex(red)}${toHex(green)}${toHex(blue)}`;
}

function dotProduct(left, right) {
    let total = 0;
    for (let index = 0; index < left.length; index += 1) {
        total += left[index] * right[index];
    }
    return total;
}

function magnitude(vector) {
    return Math.sqrt(dotProduct(vector, vector));
}

function cosineSimilarity(left, right) {
    const leftMagnitude = magnitude(left);
    const rightMagnitude = magnitude(right);
    if (!leftMagnitude || !rightMagnitude) {
        return 0;
    }
    return dotProduct(left, right) / (leftMagnitude * rightMagnitude);
}

function centerMatrix(rows) {
    if (!rows.length) {
        return [];
    }

    const width = rows[0].length;
    const means = Array.from({ length: width }, (_, columnIndex) => {
        let total = 0;
        for (const row of rows) {
            total += row[columnIndex] ?? 0;
        }
        return total / rows.length;
    });

    return rows.map((row) =>
        row.map((value, columnIndex) => (value ?? 0) - means[columnIndex])
    );
}

function gramMatrix(rows) {
    return rows.map((row) => rows.map((other) => dotProduct(row, other)));
}

function multiplyMatrixVector(matrix, vector) {
    return matrix.map((row) => dotProduct(row, vector));
}

function normalizeVector(vector) {
    const size = magnitude(vector);
    if (!size) {
        return vector.map(() => 0);
    }
    return vector.map((value) => value / size);
}

function powerIteration(matrix, orthogonalTo = []) {
    const dimension = matrix.length;
    let vector = normalizeVector(
        Array.from({ length: dimension }, (_, index) => 1 + (index % 7))
    );

    for (let iteration = 0; iteration < 64; iteration += 1) {
        let candidate = multiplyMatrixVector(matrix, vector);
        for (const basis of orthogonalTo) {
            const overlap = dotProduct(candidate, basis);
            candidate = candidate.map(
                (value, index) => value - overlap * basis[index]
            );
        }
        vector = normalizeVector(candidate);
    }

    const value = dotProduct(vector, multiplyMatrixVector(matrix, vector));
    return { value, vector };
}

function project2D(rows) {
    if (!rows.length) {
        return [];
    }

    const centeredRows = centerMatrix(rows);
    const matrix = gramMatrix(centeredRows);
    const first = powerIteration(matrix);
    const second = powerIteration(matrix, [first.vector]);
    const scales = [
        Math.sqrt(Math.max(first.value, 0)),
        Math.sqrt(Math.max(second.value, 0)),
    ];

    return rows.map((_, index) => [
        first.vector[index] * scales[0],
        second.vector[index] * scales[1],
    ]);
}

function attachPlot(items, width, height, padding) {
    const xs = items.map((item) => item.position[0]);
    const ys = items.map((item) => item.position[1]);
    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);
    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);
    const rangeX = maxX - minX || 1;
    const rangeY = maxY - minY || 1;

    return items.map((item) => ({
        ...item,
        plot: {
            x:
                padding +
                ((item.position[0] - minX) / rangeX) * (width - padding * 2),
            y:
                height -
                padding -
                ((item.position[1] - minY) / rangeY) * (height - padding * 2),
        },
    }));
}

function buildEdges(items, maxPerItem, threshold) {
    const edges = [];
    const seen = new Set();

    for (const item of items) {
        const neighbors = items
            .filter((candidate) => candidate.id !== item.id)
            .map((candidate) => ({
                id: candidate.id,
                similarity: cosineSimilarity(item.vector, candidate.vector),
            }))
            .filter((candidate) => candidate.similarity >= threshold)
            .sort((left, right) => right.similarity - left.similarity)
            .slice(0, maxPerItem);

        for (const neighbor of neighbors) {
            const key = [item.id, neighbor.id].sort().join(":");
            if (!seen.has(key)) {
                seen.add(key);
                edges.push({
                    from: item.id,
                    to: neighbor.id,
                    similarity: neighbor.similarity,
                });
            }
        }
    }

    return edges;
}

function buildParticipantEdges(items) {
    const seen = new Set();
    const edges = [];

    for (const item of items) {
        const sameCluster = items
            .filter(
                (candidate) =>
                    candidate.id !== item.id &&
                    candidate.group.internalId === item.group.internalId &&
                    candidate.group.internalId !== "none"
            )
            .map((candidate) => ({
                id: candidate.id,
                similarity: cosineSimilarity(item.vector, candidate.vector),
            }))
            .sort((left, right) => right.similarity - left.similarity)
            .slice(0, 1);

        const bridge = items
            .filter(
                (candidate) =>
                    candidate.id !== item.id &&
                    candidate.group.internalId !== item.group.internalId
            )
            .map((candidate) => ({
                id: candidate.id,
                similarity: cosineSimilarity(item.vector, candidate.vector),
            }))
            .filter((candidate) => candidate.similarity >= 0.7)
            .sort((left, right) => right.similarity - left.similarity)
            .slice(0, 1);

        for (const candidate of [...sameCluster, ...bridge]) {
            const key = [item.id, candidate.id].sort().join(":");
            if (!seen.has(key)) {
                seen.add(key);
                edges.push({
                    from: item.id,
                    to: candidate.id,
                    similarity: candidate.similarity,
                    sameCluster:
                        item.group.internalId ===
                        items.find((entry) => entry.id === candidate.id)?.group
                            .internalId,
                });
            }
        }
    }

    return edges;
}

function classifyStatementDynamics(history, statements) {
    const changes = Math.max(history.length - 1, 0);
    const leaderGap =
        statements.length >= 2
            ? statements[0].score - statements[1].score
            : (statements[0]?.score ?? 0);
    const lastHoldShare =
        history.length > 1
            ? (history.at(-1).voteCount - history.at(-2).voteCount) /
              Math.max(history.at(-1).voteCount, 1)
            : 1;

    if (changes >= 5) {
        return "volatile";
    }
    if (leaderGap < 0.12) {
        return "contested";
    }
    if (changes <= 1 || lastHoldShare > 0.45) {
        return "settled";
    }
    return "converging";
}

function classifyOpinionDynamics(groupSummaries) {
    const clustered = groupSummaries.filter((group) => !group.isUnclustered);
    const shares = clustered
        .map((group) => group.share)
        .sort((left, right) => right - left);

    if (!shares.length || shares[0] >= 0.72) {
        return "aligned";
    }
    if (shares.length === 2 && shares[0] >= 0.3 && shares[1] >= 0.3) {
        return "polarized";
    }
    if (shares[0] >= 0.45 && (shares[1] ?? 0) < 0.25) {
        return "lopsided";
    }
    if (shares.length >= 3 && (shares[2] ?? 0) >= 0.1) {
        return "fragmented";
    }
    return "diverse";
}

function pickRepresentativeParticipant(participants, primaryGroupId) {
    return (
        participants.find(
            (participant) => participant.group.internalId === primaryGroupId
        ) || participants[0]
    );
}

function buildLeaderHistory(votes, statementIds, participantGroups, scoreFor) {
    const groupedIds = [...new Set([...participantGroups.values()])].filter(
        (groupId) => groupId !== "none"
    );
    const tracker = new Map(
        statementIds.map((id) => [
            id,
            {
                agrees: 0,
                disagrees: 0,
                passes: 0,
                totalVotes: 0,
                groups: Object.fromEntries(
                    groupedIds.map((groupId) => [
                        groupId,
                        {
                            agrees: 0,
                            disagrees: 0,
                            passes: 0,
                            totalVotes: 0,
                        },
                    ])
                ),
            },
        ])
    );
    const history = [];
    let lastWinnerId = null;
    let processedVotes = 0;

    for (const vote of votes) {
        processedVotes += 1;
        const statement = tracker.get(vote.commentId);
        if (!statement) {
            continue;
        }

        const groupId = participantGroups.get(vote.voterId) || "none";
        statement.totalVotes += 1;
        if (vote.value > 0) {
            statement.agrees += 1;
        } else if (vote.value < 0) {
            statement.disagrees += 1;
        } else {
            statement.passes += 1;
        }

        if (groupId !== "none" && statement.groups[groupId]) {
            statement.groups[groupId].totalVotes += 1;
            if (vote.value > 0) {
                statement.groups[groupId].agrees += 1;
            } else if (vote.value < 0) {
                statement.groups[groupId].disagrees += 1;
            } else {
                statement.groups[groupId].passes += 1;
            }
        }

        if (processedVotes < 24) {
            continue;
        }

        if (processedVotes % 24 !== 0 && processedVotes !== votes.length) {
            continue;
        }

        const candidates = statementIds
            .map((id) => {
                const candidate = tracker.get(id);
                return {
                    id,
                    score: scoreFor(candidate),
                    totalVotes: candidate.totalVotes,
                };
            })
            .filter((candidate) => candidate.totalVotes >= 6)
            .sort((left, right) => right.score - left.score);

        if (!candidates.length) {
            continue;
        }

        const winner = candidates[0];
        if (winner.id !== lastWinnerId) {
            lastWinnerId = winner.id;
            history.push({
                statementId: winner.id,
                score: winner.score,
                voteCount: processedVotes,
                at: vote.isoTimestamp,
            });
        }
    }

    return history;
}

async function fetchText(url) {
    const response = await fetch(url);
    if (!response.ok) {
        throw new Error(`${response.status} ${response.statusText}`);
    }
    return response.text();
}

export default async function () {
    const sourceUrls = {
        summary: `${BASE_URL}/summary.csv`,
        comments: `${BASE_URL}/comments.csv`,
        votes: `${BASE_URL}/votes.csv`,
        participantVotes: `${BASE_URL}/participant-votes.csv`,
        commentGroups: `${BASE_URL}/comment-groups.csv`,
        polis: "https://polis.comhairle.scot/5ccwfj3hbe",
    };

    try {
        const [summaryText, commentsText, votesText, participantVotesText] =
            await Promise.all([
                fetchText(sourceUrls.summary),
                fetchText(sourceUrls.comments),
                fetchText(sourceUrls.votes),
                fetchText(sourceUrls.participantVotes),
            ]);

        const summary = parseSummary(summaryText);
        const comments = parseCsvObjects(commentsText).map((row) => ({
            id: row["comment-id"],
            authorId: row["author-id"],
            body: normalizeText(row["comment-body"]),
            timestamp: toInt(row.timestamp),
            isoTimestamp: new Date(toInt(row.timestamp) * 1000).toISOString(),
            agrees: toInt(row.agrees),
            disagrees: toInt(row.disagrees),
        }));
        const votes = parseCsvObjects(votesText)
            .map((row) => ({
                commentId: row["comment-id"],
                voterId: row["voter-id"],
                value: toInt(row.vote),
                timestamp: toInt(row.timestamp),
                isoTimestamp: new Date(
                    toInt(row.timestamp) * 1000
                ).toISOString(),
            }))
            .sort((left, right) => left.timestamp - right.timestamp);
        const participantRows = parseCsvObjects(participantVotesText);
        const commentIds = comments.map((comment) => comment.id);
        const commentById = Object.fromEntries(
            comments.map((comment) => [comment.id, comment])
        );

        const nonEmptyGroups = [
            ...new Set(
                participantRows
                    .map((row) => row["group-id"] || "none")
                    .filter((groupId) => groupId !== "none")
            ),
        ];
        const groupCounts = Object.fromEntries(
            nonEmptyGroups.map((groupId) => [
                groupId,
                participantRows.filter((row) => row["group-id"] === groupId)
                    .length,
            ])
        );
        const orderedGroups = nonEmptyGroups.sort(
            (left, right) => groupCounts[right] - groupCounts[left]
        );
        const groupMeta = new Map(
            orderedGroups.map((groupId, index) => {
                const style = CLUSTER_STYLES[index] || CLUSTER_STYLES.at(-1);
                return [
                    groupId,
                    {
                        internalId: groupId,
                        displayCode: style.code,
                        color: style.color,
                        soft: style.soft,
                        label: {
                            en: `Cluster ${style.code}`,
                            tw: `${style.code} 群`,
                        },
                        shortLabel: {
                            en: style.code,
                            tw: style.code,
                        },
                    },
                ];
            })
        );
        groupMeta.set("none", {
            internalId: "none",
            displayCode: UNCLUSTERED_STYLE.code,
            color: UNCLUSTERED_STYLE.color,
            soft: UNCLUSTERED_STYLE.soft,
            label: {
                en: "Unclustered",
                tw: "未分群",
            },
            shortLabel: {
                en: "U",
                tw: "U",
            },
        });

        const participantGroups = new Map(
            participantRows.map((row) => [
                row.participant,
                row["group-id"] || "none",
            ])
        );

        const statementStats = new Map(
            commentIds.map((commentId) => [
                commentId,
                {
                    id: commentId,
                    body: commentById[commentId]?.body || "",
                    createdAt: commentById[commentId]?.isoTimestamp || null,
                    createdAtDisplay: formatDatePair(
                        commentById[commentId]?.isoTimestamp || Date.now()
                    ),
                    agrees: 0,
                    disagrees: 0,
                    passes: 0,
                    totalVotes: 0,
                    groups: Object.fromEntries(
                        [...orderedGroups, "none"].map((groupId) => [
                            groupId,
                            {
                                agrees: 0,
                                disagrees: 0,
                                passes: 0,
                                totalVotes: 0,
                            },
                        ])
                    ),
                },
            ])
        );

        const participants = participantRows.map((row, index) => {
            const groupId = row["group-id"] || "none";
            const voteMap = Object.fromEntries(
                commentIds.map((commentId) => [commentId, row[commentId] || ""])
            );

            for (const commentId of commentIds) {
                const value = voteMap[commentId];
                if (value === "") {
                    continue;
                }

                const numericValue = toInt(value);
                const stats = statementStats.get(commentId);
                stats.totalVotes += 1;
                if (numericValue > 0) {
                    stats.agrees += 1;
                } else if (numericValue < 0) {
                    stats.disagrees += 1;
                } else {
                    stats.passes += 1;
                }

                const groupStats = stats.groups[groupId];
                groupStats.totalVotes += 1;
                if (numericValue > 0) {
                    groupStats.agrees += 1;
                } else if (numericValue < 0) {
                    groupStats.disagrees += 1;
                } else {
                    groupStats.passes += 1;
                }
            }

            return {
                id: row.participant,
                label: {
                    en: `Participant ${String(index + 1).padStart(2, "0")}`,
                    tw: `參與者 ${String(index + 1).padStart(2, "0")}`,
                },
                group: groupMeta.get(groupId),
                groupInternalId: groupId,
                isAuthor: toInt(row["n-comments"]) > 0,
                nComments: toInt(row["n-comments"]),
                nVotes: toInt(row["n-votes"]),
                nAgree: toInt(row["n-agree"]),
                nDisagree: toInt(row["n-disagree"]),
                nPass:
                    toInt(row["n-votes"]) -
                    toInt(row["n-agree"]) -
                    toInt(row["n-disagree"]),
                voteMap,
                vector: commentIds.map((commentId) =>
                    toInt(voteMap[commentId])
                ),
            };
        });

        const scoreFor = (stats) => {
            const supportRatio = stats.totalVotes
                ? stats.agrees / stats.totalVotes
                : 0;
            const bridgeRatios = orderedGroups
                .map((groupId) => stats.groups[groupId])
                .filter((group) => group && group.totalVotes > 0)
                .map((group) => group.agrees / group.totalVotes);
            const bridgeFloor = bridgeRatios.length
                ? Math.min(...bridgeRatios)
                : supportRatio;
            return (
                (supportRatio * 0.55 + bridgeFloor * 0.45) *
                Math.log(stats.totalVotes + 1)
            );
        };

        const statementList = [...statementStats.values()]
            .map((stats) => {
                const supportRatio = stats.totalVotes
                    ? stats.agrees / stats.totalVotes
                    : 0;
                const disagreementRatio = stats.totalVotes
                    ? stats.disagrees / stats.totalVotes
                    : 0;
                const groupSupport = [...orderedGroups, "none"].map(
                    (groupId) => {
                        const groupStats = stats.groups[groupId];
                        const total = groupStats.totalVotes;
                        const agreeRatio = total
                            ? groupStats.agrees / total
                            : 0;
                        return {
                            ...groupMeta.get(groupId),
                            agrees: groupStats.agrees,
                            disagrees: groupStats.disagrees,
                            passes: groupStats.passes,
                            totalVotes: total,
                            agreeRatio,
                            agreePct: percent(agreeRatio),
                        };
                    }
                );
                const clusteredSupport = groupSupport.filter(
                    (group) => group.internalId !== "none"
                );
                const strongestGroup =
                    clusteredSupport.reduce((best, group) =>
                        group.agreeRatio > best.agreeRatio ? group : best
                    ) || clusteredSupport[0];
                const weakestGroup =
                    clusteredSupport.reduce((best, group) =>
                        group.agreeRatio < best.agreeRatio ? group : best
                    ) || clusteredSupport[0];
                const score = scoreFor(stats);

                return {
                    id: stats.id,
                    body: stats.body,
                    createdAt: stats.createdAt,
                    createdAtDisplay: stats.createdAtDisplay,
                    agrees: stats.agrees,
                    disagrees: stats.disagrees,
                    passes: stats.passes,
                    totalVotes: stats.totalVotes,
                    supportRatio,
                    disagreementRatio,
                    supportPct: percent(supportRatio),
                    disagreementPct: percent(disagreementRatio),
                    score,
                    bridgePct: weakestGroup ? weakestGroup.agreePct : 0,
                    groupSupport,
                    strongestGroup,
                    weakestGroup,
                    vector: participants.map(
                        (participant) =>
                            toInt(participant.voteMap[stats.id]) || 0
                    ),
                };
            })
            .sort((left, right) => right.score - left.score)
            .map((statement, index, collection) => ({
                ...statement,
                rank: index + 1,
                accent: mixColors(
                    "#d6d0c7",
                    "#c4614a",
                    1 - index / Math.max(collection.length - 1, 1)
                ),
                radius: 10 + (collection.length - index) * 1.35,
            }));

        const statementById = new Map(
            statementList.map((statement) => [statement.id, statement])
        );

        const rankedStatementIds = statementList.map(
            (statement) => statement.id
        );
        for (const participant of participants) {
            participant.voteStrip = rankedStatementIds.map((statementId) => ({
                statementId,
                value: toInt(participant.voteMap[statementId]),
            }));
            participant.topAgreements = statementList
                .filter(
                    (statement) => toInt(participant.voteMap[statement.id]) > 0
                )
                .slice(0, 3)
                .map((statement) => ({
                    id: statement.id,
                    rank: statement.rank,
                    body: statement.body,
                }));
            participant.topDisagreements = statementList
                .filter(
                    (statement) => toInt(participant.voteMap[statement.id]) < 0
                )
                .slice(0, 3)
                .map((statement) => ({
                    id: statement.id,
                    rank: statement.rank,
                    body: statement.body,
                }));
            participant.leaderVote = toInt(
                participant.voteMap[statementList[0]?.id ?? ""]
            );
        }

        const statementPositions = project2D(
            statementList.map((statement) => statement.vector)
        );
        const participantPositions = project2D(
            participants.map((participant) => participant.vector)
        );
        const statementCoords = attachPlot(
            statementList.map((statement, index) => ({
                ...statement,
                id: statement.id,
                position: statementPositions[index],
            })),
            640,
            460,
            42
        );
        const participantCoords = attachPlot(
            participants.map((participant, index) => ({
                ...participant,
                position: participantPositions[index],
            })),
            640,
            460,
            42
        );

        const statementEdges = buildEdges(statementCoords, 2, 0.55).map(
            (edge) => {
                const from = statementCoords.find(
                    (statement) => statement.id === edge.from
                );
                const to = statementCoords.find(
                    (statement) => statement.id === edge.to
                );
                return {
                    ...edge,
                    x1: from.plot.x,
                    y1: from.plot.y,
                    x2: to.plot.x,
                    y2: to.plot.y,
                };
            }
        );
        const participantEdges = buildParticipantEdges(participantCoords).map(
            (edge) => {
                const from = participantCoords.find(
                    (participant) => participant.id === edge.from
                );
                const to = participantCoords.find(
                    (participant) => participant.id === edge.to
                );
                return {
                    ...edge,
                    x1: from.plot.x,
                    y1: from.plot.y,
                    x2: to.plot.x,
                    y2: to.plot.y,
                };
            }
        );

        const groupSummaries = [...orderedGroups, "none"].map((groupId) => {
            const members = participantCoords.filter(
                (participant) => participant.groupInternalId === groupId
            );
            const share =
                members.length / Math.max(participantCoords.length, 1);
            const standoutStatements = statementList
                .map((statement) => {
                    const groupStats = statement.groupSupport.find(
                        (group) => group.internalId === groupId
                    );
                    const distinctiveness = groupStats
                        ? groupStats.agreeRatio - statement.supportRatio
                        : -1;
                    return {
                        id: statement.id,
                        rank: statement.rank,
                        body: statement.body,
                        distinctiveness,
                    };
                })
                .filter((statement) => statement.distinctiveness > 0)
                .sort(
                    (left, right) =>
                        right.distinctiveness - left.distinctiveness
                )
                .slice(0, 3);

            return {
                ...groupMeta.get(groupId),
                isUnclustered: groupId === "none",
                count: members.length,
                share,
                sharePct: percent(share),
                standoutStatements,
            };
        });

        const leaderHistory = buildLeaderHistory(
            votes,
            commentIds,
            participantGroups,
            scoreFor
        )
            .map((event) => ({
                ...event,
                statement: statementById.get(event.statementId),
                atDisplay: formatDateTimePair(event.at),
            }))
            .filter((event) => event.statement);

        const statementDynamics = classifyStatementDynamics(
            leaderHistory,
            statementList
        );
        const opinionDynamics = classifyOpinionDynamics(groupSummaries);
        const primaryGroupId = groupSummaries.find(
            (group) => !group.isUnclustered
        )?.internalId;
        const featuredParticipant = pickRepresentativeParticipant(
            participantCoords,
            primaryGroupId
        );

        const firstActivity = new Date(
            Math.min(
                ...comments.map((comment) => comment.timestamp),
                ...votes.map((vote) => vote.timestamp)
            ) * 1000
        );
        const lastActivity = new Date(
            Math.max(...votes.map((vote) => vote.timestamp)) * 1000
        );

        return {
            ok: true,
            exportId: EXPORT_ID,
            sourceUrls,
            polisUrl: sourceUrls.polis,
            question: {
                en: "What kind of AI use would people accept in care, government, and everyday public life?",
                tw: "人們願意接受哪一種 AI 應用於照護、政府與日常公共生活？",
            },
            dek: {
                en: "A Habermolt-style deliberation view rebuilt from Polis exports only. The page below uses vote vectors, cross-group support, and local inference rather than hidden APIs or agent metadata.",
                tw: "這是一個只靠 Polis 匯出資料重建的 Habermolt 風格審議頁面。下方內容以投票向量、跨群支持度與本地推導為基礎，沒有使用隱藏 API 或智慧體中介資料。",
            },
            summary: {
                voters: toInt(summary.voters),
                votersInConversation: toInt(summary["voters-in-conv"]),
                comments: toInt(summary.comments),
                groups: toInt(summary.groups),
                commenters: toInt(summary.commenters),
            },
            stats: {
                participants: participantCoords.length,
                votes: votes.length,
                statements: statementList.length,
                clusters: orderedGroups.length,
                clusteredParticipants:
                    participantCoords.length -
                    (groupSummaries.find((group) => group.isUnclustered)
                        ?.count || 0),
            },
            sourceWindow: {
                from: formatDatePair(firstActivity),
                to: formatDatePair(lastActivity),
            },
            leadingStatement: statementCoords[0],
            statements: statementCoords,
            statementEdges,
            participants: participantCoords.sort((left, right) => {
                if (left.group.displayCode === right.group.displayCode) {
                    return Number(left.id) - Number(right.id);
                }
                return left.group.displayCode.localeCompare(
                    right.group.displayCode
                );
            }),
            participantEdges,
            groups: groupSummaries,
            leaderHistory,
            statementDynamics,
            opinionDynamics,
            featuredParticipantId: featuredParticipant?.id || null,
            method: {
                en: [
                    "Comments become statements.",
                    "The leading statement is ranked by overall support plus the weakest support across discovered Polis clusters.",
                    "The statement and participant maps are simple two-dimensional projections of vote vectors, so proximity means similar voting patterns, not exact ideological distance.",
                    "What is missing compared with Habermolt: agent names, authored opinions, semantic embeddings, and native ranking history.",
                ],
                tw: [
                    "每則 comment 都視為一條 statement。",
                    "領先陳述的排序，結合了整體支持度與各 Polis 分群中最弱的一段支持度。",
                    "陳述地圖與參與者地圖，都是對投票向量的簡易二維投影；因此接近代表投票模式相似，而不是精確的意識形態距離。",
                    "與 Habermolt 相比，這裡缺少的是：智慧體名稱、撰寫出的意見、語意嵌入，以及原生的排序歷史。",
                ],
            },
        };
    } catch (error) {
        return {
            ok: false,
            exportId: EXPORT_ID,
            sourceUrls,
            polisUrl: sourceUrls.polis,
            error: String(error),
        };
    }
}
