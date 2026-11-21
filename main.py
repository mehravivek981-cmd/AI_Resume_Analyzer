import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import font as tkfont

from resume_parser import extract_resume_text, extract_candidate_name
from resume_analysis import analyze_resume
from job_finder import find_jobs
from company_finder import find_companies

# ------------------------------------------------------------------
# Theme
# ------------------------------------------------------------------
BG = "#F3F5F9"
CARD = "#FFFFFF"
INK = "#101828"
MUTED = "#667085"
LINE = "#E4E7EC"
ACCENT = "#0B7285"
ACCENT_DARK = "#095C6B"
ACCENT_SOFT = "#E3F4F7"
GOOD = "#2F9E44"
WARN = "#F08C00"
BAD = "#E03131"
HEADER = "#0F1B2D"


def pick_font():
    available = set(tkfont.families())
    for name in ("Segoe UI", "Inter", "SF Pro Text", "Helvetica Neue",
                 "Ubuntu", "DejaVu Sans", "Arial"):
        if name in available:
            return name
    return "TkDefaultFont"


class ScrollFrame(tk.Frame):
    """A frame whose content scrolls vertically (mouse wheel supported)."""

    def __init__(self, parent, bg=BG):
        super().__init__(parent, bg=bg)
        self.canvas = tk.Canvas(self, bg=bg, highlightthickness=0, bd=0)
        self.bar = tk.Scrollbar(self, orient="vertical",
                                command=self.canvas.yview, width=10)
        self.inner = tk.Frame(self.canvas, bg=bg)
        self._win = self.canvas.create_window((0, 0), window=self.inner,
                                              anchor="nw")
        self.canvas.configure(yscrollcommand=self.bar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.bar.pack(side="right", fill="y")

        self.inner.bind("<Configure>", lambda e: self.canvas.configure(
            scrollregion=self.canvas.bbox("all")))
        self.canvas.bind("<Configure>", lambda e: self.canvas.itemconfigure(
            self._win, width=e.width))

        for w in (self.canvas, self.inner):
            w.bind("<Enter>", self._bind_wheel)
            w.bind("<Leave>", self._unbind_wheel)

    def _bind_wheel(self, _):
        self.canvas.bind_all("<MouseWheel>", self._on_wheel)
        self.canvas.bind_all("<Button-4>", self._on_wheel)
        self.canvas.bind_all("<Button-5>", self._on_wheel)

    def _unbind_wheel(self, _):
        self.canvas.unbind_all("<MouseWheel>")
        self.canvas.unbind_all("<Button-4>")
        self.canvas.unbind_all("<Button-5>")

    def _on_wheel(self, event):
        if self.inner.winfo_reqheight() <= self.canvas.winfo_height():
            return
        if event.num == 4:
            self.canvas.yview_scroll(-2, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(2, "units")
        else:
            self.canvas.yview_scroll(int(-event.delta / 60) or -1, "units")

    def clear(self):
        for child in self.inner.winfo_children():
            child.destroy()
        self.canvas.yview_moveto(0)


class ResumeAnalyzer:

    def __init__(self, root):
        self.root = root
        root.title("AI Resume Analyzer")
        root.geometry("1180x720")
        root.minsize(1000, 620)
        root.configure(bg=BG)

        self.F = pick_font()
        self.resume_text = ""
        self.candidate_name = "Candidate"
        self.jobs = []
        self.job_cards = []
        self.selected_job = None

        self._build_header()
        self._build_body()
        self._show_empty_profile()
        self._show_empty_jobs()
        self._show_empty_companies()

    # ------------------------------------------------------------
    # Small helpers
    # ------------------------------------------------------------
    def font(self, size=10, weight="normal"):
        return (self.F, size, weight)

    def button(self, parent, text, command, primary=True):
        bg, fg, hover = ((ACCENT, "white", ACCENT_DARK) if primary
                         else (CARD, INK, ACCENT_SOFT))
        btn = tk.Label(parent, text=text, font=self.font(10, "bold"), bg=bg,
                       fg=fg, padx=18, pady=8, cursor="hand2")
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e: btn.config(bg=hover))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg))
        return btn

    def card(self, parent, **pack):
        outer = tk.Frame(parent, bg=LINE)
        outer.pack(fill="x", **pack)
        inner = tk.Frame(outer, bg=CARD, padx=16, pady=14)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        return outer, inner

    def chips(self, parent, items, fg, bg, max_width=290):
        """Wrapping row of small tags."""
        f = tkfont.Font(family=self.F, size=9)
        row = tk.Frame(parent, bg=parent["bg"])
        row.pack(anchor="w", fill="x")
        used = 0
        for item in items:
            w = f.measure(item) + 24
            if used + w > max_width and used > 0:
                row = tk.Frame(parent, bg=parent["bg"])
                row.pack(anchor="w", fill="x", pady=(5, 0))
                used = 0
            tk.Label(row, text=item, font=self.font(9), fg=fg, bg=bg,
                     padx=8, pady=3).pack(side="left", padx=(0, 5))
            used += w + 5

    def section_title(self, parent, text, top=16):
        tk.Label(parent, text=text, font=self.font(10, "bold"), fg=INK,
                 bg=parent["bg"]).pack(anchor="w", pady=(top, 6))

    def empty_state(self, parent, title, body):
        box = tk.Frame(parent, bg=parent["bg"])
        box.pack(fill="x", pady=60, padx=20)
        tk.Label(box, text=title, font=self.font(12, "bold"), fg=INK,
                 bg=parent["bg"]).pack()
        tk.Label(box, text=body, font=self.font(10), fg=MUTED,
                 bg=parent["bg"], wraplength=240,
                 justify="center").pack(pady=(6, 0))

    # ------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------
    def _build_header(self):
        bar = tk.Frame(self.root, bg=HEADER, height=72)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        left = tk.Frame(bar, bg=HEADER)
        left.pack(side="left", padx=28)
        tk.Label(left, text="Resume Analyzer", font=self.font(18, "bold"),
                 fg="white", bg=HEADER).pack(anchor="w", pady=(12, 0))
        tk.Label(left, text="Upload a PDF resume, see your score, and find "
                            "roles and companies that fit.",
                 font=self.font(9), fg="#9FB3C8", bg=HEADER).pack(anchor="w")

        right = tk.Frame(bar, bg=HEADER)
        right.pack(side="right", padx=28)
        self.status = tk.Label(right, text="No resume loaded",
                               font=self.font(9), fg="#9FB3C8", bg=HEADER)
        self.status.pack(side="left", padx=(0, 16))
        self.button(right, "Upload Resume", self.upload_resume).pack(side="left")

    def _build_body(self):
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True, padx=20, pady=16)
        body.columnconfigure(0, weight=0, minsize=340)
        body.columnconfigure(1, weight=1, uniform="cols")
        body.columnconfigure(2, weight=1, uniform="cols")
        body.rowconfigure(0, weight=1)

        self.profile = self._panel(body, 0, "Your profile")
        self.jobs_panel = self._panel(body, 1, "Recommended roles")
        self.company_panel = self._panel(body, 2, "Companies")

    def _panel(self, parent, col, title):
        wrap = tk.Frame(parent, bg=BG)
        wrap.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 12, 0))
        title_lbl = tk.Label(wrap, text=title, font=self.font(12, "bold"),
                             fg=INK, bg=BG)
        title_lbl.pack(anchor="w", pady=(0, 8))
        sf = ScrollFrame(wrap)
        sf.pack(fill="both", expand=True)
        sf.title_label = title_lbl
        return sf

    # ------------------------------------------------------------
    # Empty states
    # ------------------------------------------------------------
    def _show_empty_profile(self):
        self.profile.clear()
        self.empty_state(self.profile.inner, "No resume yet",
                         "Choose a text-based PDF resume to see your score, "
                         "skills and improvement tips.")

    def _show_empty_jobs(self):
        self.jobs_panel.clear()
        self.empty_state(self.jobs_panel.inner, "Roles will appear here",
                         "Matches are ranked by how many required skills "
                         "your resume already covers.")

    def _show_empty_companies(self):
        self.company_panel.title_label.config(text="Companies")
        self.company_panel.clear()
        self.empty_state(self.company_panel.inner, "Pick a role",
                         "Select a recommended role to see companies hiring "
                         "for it.")

    # ------------------------------------------------------------
    # Upload & analysis
    # ------------------------------------------------------------
    def upload_resume(self):
        path = filedialog.askopenfilename(
            title="Select resume", filetypes=[("PDF files", "*.pdf")])
        if not path:
            return

        try:
            self.resume_text = extract_resume_text(path)
            self.candidate_name = extract_candidate_name(self.resume_text)
            analysis = analyze_resume(self.resume_text)
            self.jobs = find_jobs(self.resume_text)
        except Exception as e:
            messagebox.showerror("Resume error",
                                 f"Unable to process resume:\n{e}")
            return

        self.status.config(text=f"Loaded: {path.replace(chr(92), '/').split('/')[-1]}",
                           fg="#8CE0A6")
        self.selected_job = None
        self._render_profile(analysis)
        self._render_jobs()
        self._show_empty_companies()

    # ------------------------------------------------------------
    # Profile panel
    # ------------------------------------------------------------
    def _render_profile(self, a):
        p = self.profile
        p.clear()

        _, c = self.card(p.inner, pady=(0, 10))
        tk.Label(c, text=self.candidate_name, font=self.font(15, "bold"),
                 fg=INK, bg=CARD, wraplength=270,
                 justify="left").pack(anchor="w")
        tk.Label(c, text="Candidate", font=self.font(9), fg=MUTED,
                 bg=CARD).pack(anchor="w", pady=(0, 10))

        score = a["score"]
        color = GOOD if score >= 75 else WARN if score >= 50 else BAD
        label = ("Strong" if score >= 75 else
                 "Decent" if score >= 50 else "Needs work")

        ring_row = tk.Frame(c, bg=CARD)
        ring_row.pack(anchor="w", fill="x")
        ring = tk.Canvas(ring_row, width=110, height=110, bg=CARD,
                         highlightthickness=0)
        ring.pack(side="left")
        ring.create_oval(10, 10, 100, 100, outline=LINE, width=10)
        ring.create_arc(10, 10, 100, 100, start=90,
                        extent=-max(1, score) * 3.6, style="arc",
                        outline=color, width=10)
        ring.create_text(55, 55, text=str(score), fill=INK,
                         font=self.font(24, "bold"))

        txt = tk.Frame(ring_row, bg=CARD)
        txt.pack(side="left", padx=14)
        tk.Label(txt, text="Resume score", font=self.font(9), fg=MUTED,
                 bg=CARD).pack(anchor="w")
        tk.Label(txt, text=label, font=self.font(14, "bold"), fg=color,
                 bg=CARD).pack(anchor="w")
        tk.Label(txt, text="out of 100", font=self.font(9), fg=MUTED,
                 bg=CARD).pack(anchor="w")

        # Skills
        _, c = self.card(p.inner, pady=(0, 10))
        self.section_title(c, f"Skills detected ({len(a['skills'])})", top=0)
        if a["skills"]:
            self.chips(c, a["skills"], ACCENT, ACCENT_SOFT)
        else:
            tk.Label(c, text="No known skills found in the text.",
                     font=self.font(9), fg=MUTED, bg=CARD).pack(anchor="w")

        # Experience
        _, c = self.card(p.inner, pady=(0, 10))
        self.section_title(c, "Experience mentions", top=0)
        lines = [ln for ln in a["experience"].splitlines() if ln.strip()][:5]
        for ln in lines:
            ln = ln if len(ln) < 70 else ln[:67] + "..."
            tk.Label(c, text=ln, font=self.font(9), fg=MUTED, bg=CARD,
                     wraplength=270, justify="left").pack(anchor="w", pady=1)

        # Tips
        _, c = self.card(p.inner, pady=(0, 10))
        self.section_title(c, "How to improve", top=0)
        for tip in a["tips"]:
            row = tk.Frame(c, bg=CARD)
            row.pack(anchor="w", fill="x", pady=3)
            tk.Label(row, text="•", font=self.font(10, "bold"), fg=ACCENT,
                     bg=CARD).pack(side="left", anchor="n")
            tk.Label(row, text=tip, font=self.font(9), fg=INK, bg=CARD,
                     wraplength=262, justify="left").pack(side="left",
                                                          padx=(6, 0))

    # ------------------------------------------------------------
    # Jobs panel
    # ------------------------------------------------------------
    def _render_jobs(self):
        p = self.jobs_panel
        p.clear()
        self.job_cards = []

        if not self.jobs:
            self.empty_state(p.inner, "No matches", "No job recommendations "
                                                    "were found.")
            return

        for job in self.jobs:
            outer, c = self.card(p.inner, pady=(0, 10))
            tk.Label(c, text=job["title"], font=self.font(12, "bold"),
                     fg=INK, bg=CARD).pack(anchor="w")

            m = job["match"]
            color = GOOD if m >= 70 else WARN if m >= 40 else BAD
            bar = tk.Canvas(c, height=8, bg=CARD, highlightthickness=0)
            bar.pack(fill="x", pady=(8, 2))
            bar.bind("<Configure>", lambda e, b=bar, m=m, col=color:
                     self._draw_bar(b, m, col))
            tk.Label(c, text=f"{m:.0f}% match", font=self.font(9, "bold"),
                     fg=color, bg=CARD).pack(anchor="w")

            if job["matched"]:
                self.section_title(c, "You have", top=10)
                self.chips(c, job["matched"], GOOD, "#E6F6EA", max_width=250)
            if job["missing"]:
                self.section_title(c, "To learn", top=10)
                self.chips(c, job["missing"], "#B54708", "#FFF1DB",
                           max_width=250)

            self._make_clickable(outer, lambda j=job: self.select_job(j))
            self.job_cards.append((job, outer))

    @staticmethod
    def _draw_bar(canvas, pct, color):
        canvas.delete("all")
        w = canvas.winfo_width()
        canvas.create_rectangle(0, 0, w, 8, fill=LINE, outline=LINE)
        canvas.create_rectangle(0, 0, w * pct / 100, 8, fill=color,
                                outline=color)

    def _make_clickable(self, widget, callback):
        widget.configure(cursor="hand2")
        widget.bind("<Button-1>", lambda e: callback())
        for child in widget.winfo_children():
            self._make_clickable(child, callback)

    def select_job(self, job):
        self.selected_job = job["title"]
        for j, outer in self.job_cards:
            outer.config(bg=ACCENT if j is job else LINE)
        self._render_companies(job["title"])

    # ------------------------------------------------------------
    # Companies panel
    # ------------------------------------------------------------
    def _render_companies(self, role):
        p = self.company_panel
        p.title_label.config(text=f"Companies hiring: {role}")
        p.clear()

        try:
            companies = find_companies(role)
        except Exception as e:
            messagebox.showerror("Company finder error", str(e))
            return

        if not companies:
            self.empty_state(p.inner, "No companies found",
                             "There are no companies listed for this role "
                             "in companies.csv yet.")
            return

        for comp in companies:
            _, c = self.card(p.inner, pady=(0, 10))
            row = tk.Frame(c, bg=CARD)
            row.pack(fill="x")

            initial = (comp["company"][:1] or "?").upper()
            tk.Label(row, text=initial, font=self.font(14, "bold"),
                     fg=ACCENT, bg=ACCENT_SOFT, width=3,
                     height=1, pady=6).pack(side="left", anchor="n")

            info = tk.Frame(row, bg=CARD)
            info.pack(side="left", padx=12, fill="x", expand=True)
            tk.Label(info, text=comp["company"], font=self.font(11, "bold"),
                     fg=INK, bg=CARD).pack(anchor="w")
            tk.Label(info, text=comp["location"], font=self.font(9),
                     fg=MUTED, bg=CARD).pack(anchor="w")
            tk.Label(info, text=comp["description"], font=self.font(9),
                     fg=INK, bg=CARD, wraplength=250,
                     justify="left").pack(anchor="w", pady=(4, 0))


if __name__ == "__main__":
    root = tk.Tk()
    ResumeAnalyzer(root)
    root.mainloop()
