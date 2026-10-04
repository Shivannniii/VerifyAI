import { useEffect, useMemo, useState } from "react";
import {
    FileCheck2,
    FileText,
    Plus,
    Search,
    Upload,
} from "lucide-react";
import { Link } from "react-router-dom";
import { api } from "../api";

export default function Research() {
    const [papers, setPapers] = useState([]);
    const [query, setQuery] = useState("");
    const [busy, setBusy] = useState(false);
    const [error, setError] = useState("");
    const [text, setText] = useState("");
    const [showText, setShowText] = useState(false);

    const load = async () => {
        try {
            setError("");
            const data = await api.listPapers();
            setPapers(Array.isArray(data) ? data : []);
        } catch (e) {
            setError(e?.message || "Failed to load research papers.");
        }
    };

    // IMPORTANT:
    // Do not use `useEffect(load, [])` here because load() is async
    // and returns a Promise. React expects an optional cleanup function.
    useEffect(() => {
        load();
    }, []);

    const filtered = useMemo(() => {
        const normalizedQuery = query.toLowerCase().trim();

        if (!normalizedQuery) {
            return papers;
        }

        return papers.filter((paper) =>
            (paper.filename || "").toLowerCase().includes(normalizedQuery)
        );
    }, [papers, query]);

    async function upload(e) {
        const file = e.target.files?.[0];

        if (!file) {
            return;
        }

        setBusy(true);
        setError("");

        try {
            const result = await api.uploadPdf(file);

            await api.analyze(result.research_id);

            await load();
        } catch (e) {
            setError(e?.message || "Failed to upload and analyze the PDF.");
        } finally {
            setBusy(false);

            // Allow the same file to be selected again later.
            e.target.value = "";
        }
    }

    async function submit() {
        if (text.trim().length < 80) {
            setError("Please enter at least 80 characters of research text.");
            return;
        }

        setBusy(true);
        setError("");

        try {
            const result = await api.submitText(
                text.trim(),
                "Pasted research"
            );

            await api.analyze(result.research_id);

            setText("");
            setShowText(false);

            await load();
        } catch (e) {
            setError(e?.message || "Failed to analyze the research text.");
        } finally {
            setBusy(false);
        }
    }

    return (
        <div className="page">
            {/* PAGE HEADER */}
            <div className="page-header">
                <div>
                    <h1>Research Verification</h1>

                    <p>
                        Upload a paper, extract claims, then inspect evidence and
                        verdicts.
                    </p>
                </div>

                <button
                    className="btn btn-primary"
                    onClick={() => {
                        setError("");
                        setShowText(true);
                    }}
                    disabled={busy}
                >
                    <Plus size={16} />
                    New text analysis
                </button>
            </div>

            {/* ERROR */}
            {error && (
                <div className="form-error">
                    {error}
                </div>
            )}

            {/* INPUT WORKSPACE */}
            <div
                className="card"
                style={{
                    padding: 20,
                    marginBottom: 16,
                }}
            >
                <div
                    className="input-workspace"
                    style={{
                        gridTemplateColumns: "1fr 1fr",
                    }}
                >
                    {/* PDF UPLOAD */}
                    <label
                        className="upload-zone"
                        style={{
                            minHeight: 180,
                            cursor: busy ? "not-allowed" : "pointer",
                            opacity: busy ? 0.7 : 1,
                        }}
                    >
                        <div>
                            <div className="upload-icon">
                                <Upload size={22} />
                            </div>

                            <strong>
                                {busy
                                    ? "Processing..."
                                    : "Drop a research PDF or choose file"}
                            </strong>

                            <p
                                style={{
                                    color: "var(--muted)",
                                    fontSize: 12,
                                }}
                            >
                                Up to 20 MB
                            </p>

                            <span className="btn btn-secondary">
                                Choose PDF

                                <input
                                    hidden
                                    type="file"
                                    accept=".pdf,application/pdf"
                                    onChange={upload}
                                    disabled={busy}
                                />
                            </span>
                        </div>
                    </label>

                    {/* TEXT INPUT */}
                    <div
                        style={{
                            display: "flex",
                            flexDirection: "column",
                            justifyContent: "center",
                            padding: 10,
                        }}
                    >
                        <span
                            className="eyebrow"
                            style={{
                                width: "fit-content",
                            }}
                        >
                            Evidence-first
                        </span>

                        <h2
                            style={{
                                margin: "15px 0 7px",
                                fontSize: 22,
                                letterSpacing: "-.04em",
                            }}
                        >
                            Start with the evidence.
                        </h2>

                        <p
                            style={{
                                color: "var(--muted)",
                                fontSize: 12,
                                lineHeight: 1.7,
                            }}
                        >
                            Claim extraction is automatic; scholarly checking can
                            use the baseline engine or Gemini when configured.
                        </p>

                        {showText && (
                            <>
                                <textarea
                                    className="textarea"
                                    style={{
                                        minHeight: 120,
                                    }}
                                    value={text}
                                    onChange={(e) => setText(e.target.value)}
                                    placeholder="Paste at least a few sentences..."
                                    disabled={busy}
                                />

                                <button
                                    className="btn btn-primary"
                                    style={{
                                        width: "fit-content",
                                        marginTop: 8,
                                    }}
                                    disabled={busy || text.trim().length < 80}
                                    onClick={submit}
                                >
                                    {busy ? "Analyzing..." : "Analyze pasted text"}
                                </button>
                            </>
                        )}
                    </div>
                </div>
            </div>

            {/* RESEARCH PAPERS */}
            <div className="card table-card">
                <div
                    style={{
                        padding: 14,
                        borderBottom: "1px solid var(--line)",
                    }}
                >
                    <div
                        className="search-box"
                        style={{
                            width: "100%",
                        }}
                    >
                        <Search size={14} />

                        <input
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search research papers..."
                        />
                    </div>
                </div>

                <table className="table">
                    <thead>
                        <tr>
                            <th>Paper</th>
                            <th>Status</th>
                            <th>Claims</th>
                            <th>Checked</th>
                            <th></th>
                        </tr>
                    </thead>

                    <tbody>
                        {filtered.length === 0 ? (
                            <tr>
                                <td
                                    colSpan={5}
                                    style={{
                                        textAlign: "center",
                                        padding: 30,
                                        color: "var(--muted)",
                                    }}
                                >
                                    {query
                                        ? "No research papers match your search."
                                        : "No research papers yet. Upload a PDF or analyze some text to get started."}
                                </td>
                            </tr>
                        ) : (
                            filtered.map((paper) => (
                                <tr key={paper.id}>
                                    <td>
                                        <div
                                            style={{
                                                display: "flex",
                                                gap: 10,
                                                alignItems: "center",
                                            }}
                                        >
                                            <div className="activity-icon">
                                                <FileText size={16} />
                                            </div>

                                            <div>
                                                <strong>
                                                    {paper.filename || "Untitled research"}
                                                </strong>
                                            </div>
                                        </div>
                                    </td>

                                    <td>
                                        <span className="pill success">
                                            {paper.status || "pending"}
                                        </span>
                                    </td>

                                    <td>
                                        {paper.claim_count ?? 0}
                                    </td>

                                    <td>
                                        {paper.verified_count ?? 0}
                                    </td>

                                    <td>
                                        <Link
                                            to={`/app/research/${paper.id}`}
                                            className="btn btn-ghost"
                                            style={{
                                                minHeight: 34,
                                            }}
                                        >
                                            Open
                                            <FileCheck2 size={14} />
                                        </Link>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}