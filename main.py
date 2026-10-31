
import os
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

from resume_parser import extract_resume_text
from resume_analysis import analyze_resume
from job_finder import find_jobs


BG = "#F3F6FB"
SIDEBAR = "#172554"
WHITE = "#FFFFFF"
BLUE = "#2563EB"
GREEN = "#16A34A"
PURPLE = "#7C3AED"
ORANGE = "#EA580C"
TEAL = "#0F766E"
RED = "#DC2626"
TEXT = "#1E293B"
GRAY = "#64748B"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JOBS_FILE = os.path.join(BASE_DIR, "jobs.csv")


class ResumeAnalyzerApp:

    def __init__(self, root):

        self.root = root

        self.root.title("AI Resume Analyzer & Smart Job Finder")
        self.root.geometry("1100x720")
        self.root.minsize(850, 600)
        self.root.configure(bg=BG)

        self.resume_path = ""
        self.resume_text = ""
        self.analysis = None
        self.recommendations = None

        self.create_gui()


    def create_gui(self):

                        
        main_frame = tk.Frame(self.root, bg=BG)
        main_frame.pack(fill="both", expand=True)


        sidebar = tk.Frame(
            main_frame,
            bg=SIDEBAR,
            width=240
        )

        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(
            sidebar,
            text="AI RESUME",
            font=("Arial", 22, "bold"),
            fg=WHITE,
            bg=SIDEBAR
        ).pack(pady=(35, 5))

        tk.Label(
            sidebar,
            text="ANALYZER",
            font=("Arial", 17, "bold"),
            fg="#60A5FA",
            bg=SIDEBAR
        ).pack()

        tk.Label(
            sidebar,
            text="Smart Job Finder",
            font=("Arial", 10),
            fg="#CBD5E1",
            bg=SIDEBAR
        ).pack(pady=10)

        tk.Label(
            sidebar,
            text="MAIN MENU",
            font=("Arial", 10, "bold"),
            fg="#93C5FD",
            bg=SIDEBAR
        ).pack(anchor="w", padx=22, pady=(35, 12))

                              

        self.create_button(
            sidebar, "1. Upload Resume",
            BLUE, self.upload_resume
        )

        self.create_button(
            sidebar, "2. Analyze Resume",
            GREEN, self.analyze
        )

        self.create_button(
            sidebar, "3. Find Jobs",
            PURPLE, self.show_jobs
        )

        self.create_button(
            sidebar, "4. Resume Score",
            ORANGE, self.show_score
        )

        self.create_button(
            sidebar, "5. Improvement Tips",
            TEAL, self.show_tips
        )

        self.create_button(
            sidebar, "6. Clear Results",
            RED, self.clear_results
        )

        tk.Label(
            sidebar,
            text="AI Resume Analyzer\nVersion 1.0",
            font=("Arial", 9),
            fg="#CBD5E1",
            bg=SIDEBAR,
            justify="center"
        ).pack(side="bottom", pady=25)


        content = tk.Frame(main_frame, bg=BG)
        content.pack(
            side="right",
            fill="both",
            expand=True,
            padx=22,
            pady=20
        )


        tk.Label(
            content,
            text="Dashboard",
            font=("Arial", 25, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Analyze your resume and discover suitable job opportunities.",
            font=("Arial", 11),
            fg=GRAY,
            bg=BG
        ).pack(anchor="w", pady=(5, 18))


        welcome = tk.Frame(
            content,
            bg=WHITE,
            padx=18,
            pady=15
        )

        welcome.pack(fill="x", pady=(0, 15))

        tk.Label(
            welcome,
            text="Welcome to AI Resume Analyzer!",
            font=("Arial", 16, "bold"),
            fg=BLUE,
            bg=WHITE
        ).pack(anchor="w")

        tk.Label(
            welcome,
            text="Upload your PDF resume and get automatic analysis.",
            font=("Arial", 10),
            fg=GRAY,
            bg=WHITE
        ).pack(anchor="w", pady=5)

        self.file_label = tk.Label(
            welcome,
            text="No resume selected",
            font=("Arial", 10, "bold"),
            fg=ORANGE,
            bg=WHITE
        )

        self.file_label.pack(anchor="w", pady=5)

                                                          

        cards = tk.Frame(content, bg=BG)
        cards.pack(fill="x", pady=5)

        self.create_card(
            cards, "RESUME SCORE", "--", BLUE
        )

        self.create_card(
            cards, "SKILLS FOUND", "--", GREEN
        )

        self.create_card(
            cards, "JOB MATCHES", "--", PURPLE
        )

                                                            

        tk.Label(
            content,
            text="Analysis Results",
            font=("Arial", 16, "bold"),
            fg=TEXT,
            bg=BG
        ).pack(anchor="w", pady=(15, 8))

        output_frame = tk.Frame(
            content,
            bg=WHITE,
            padx=10,
            pady=10
        )

        output_frame.pack(fill="both", expand=True)

        self.output = scrolledtext.ScrolledText(
            output_frame,
            font=("Consolas", 10),
            bg=WHITE,
            fg=TEXT,
            wrap=tk.WORD,
            relief="flat",
            padx=12,
            pady=12
        )

        self.output.pack(fill="both", expand=True)

        self.output.insert(
            tk.END,
            "WELCOME!\n\n"
            "Please follow these steps:\n\n"
            "1. Upload your PDF resume.\n"
            "2. Click Analyze Resume.\n"
            "3. Check your resume score.\n"
            "4. Find suitable jobs.\n"
            "5. View improvement tips.\n\n"
            "Your results will appear here."
        )

        self.score_value = None
        self.skills_value = None
        self.jobs_value = None

                                                         

    def create_button(self, parent, text, color, command):

        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=color,
            activeforeground=WHITE,
            font=("Arial", 10, "bold"),
            relief="flat",
            cursor="hand2",
            padx=10,
            pady=12
        )

        button.pack(fill="x", padx=15, pady=6)

                                                      

    def create_card(self, parent, title, value, color):

        card = tk.Frame(
            parent,
            bg=WHITE,
            padx=15,
            pady=15,
            highlightbackground=color,
            highlightthickness=2
        )

        card.pack(
            side="left",
            fill="both",
            expand=True,
            padx=5
        )

        tk.Label(
            card,
            text=title,
            font=("Arial", 9, "bold"),
            bg=WHITE,
            fg=GRAY
        ).pack()

        value_label = tk.Label(
            card,
            text=value,
            font=("Arial", 22, "bold"),
            bg=WHITE,
            fg=color
        )

        value_label.pack(pady=5)

        if title == "RESUME SCORE":
            self.score_value = value_label

        elif title == "SKILLS FOUND":
            self.skills_value = value_label

        elif title == "JOB MATCHES":
            self.jobs_value = value_label

                                                       

    def upload_resume(self):

        file_path = filedialog.askopenfilename(
            title="Select Resume PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if file_path:

            self.resume_path = file_path
            self.resume_text = ""
            self.analysis = None
            self.recommendations = None

            self.file_label.config(
                text="Selected: " + os.path.basename(file_path),
                fg=GREEN
            )

            self.reset_cards()

            self.output.delete("1.0", tk.END)

            self.output.insert(
                tk.END,
                "Resume uploaded successfully!\n\n"
                "Now click Analyze Resume."
            )

                                                     

    def load_analysis(self):

        if not self.resume_path:
            messagebox.showwarning(
                "Warning",
                "Please upload your resume first."
            )
            return False

        if not os.path.isfile(JOBS_FILE):
            messagebox.showerror(
                "Error",
                "jobs.csv file not found."
            )
            return False

        if self.analysis is None:

            self.resume_text = extract_resume_text(
                self.resume_path
            )

            self.analysis = analyze_resume(
                self.resume_text
            )

        return True

                                                        

    def analyze(self):

        try:

            if not self.load_analysis():
                return

            data = self.analysis

            self.output.delete("1.0", tk.END)

            self.output.insert(
                tk.END,
                "========== RESUME ANALYSIS ==========\n\n"
            )

            self.output.insert(
                tk.END,
                f"Resume Score: {data['score']}/100\n\n"
            )

            self.output.insert(
                tk.END,
                "DETECTED SKILLS:\n"
            )

            for skill in data["skills"]:
                self.output.insert(
                    tk.END,
                    f"  - {skill}\n"
                )

            self.output.insert(
                tk.END,
                "\nEXPERIENCE:\n"
                + data["experience"] + "\n"
            )

            self.output.insert(
                tk.END,
                "\nAnalysis completed successfully!"
            )

            self.update_cards()

        except Exception as error:

            messagebox.showerror(
                "Analysis Error",
                str(error)
            )

                                                   

    def show_jobs(self):

        try:

            if not self.load_analysis():
                return

            if self.recommendations is None:

                self.recommendations = find_jobs(
                    self.resume_text,
                    csv_path=JOBS_FILE,
                    top_n=5
                )

            self.output.delete("1.0", tk.END)

            self.output.insert(
                tk.END,
                "========== JOB RECOMMENDATIONS ==========\n\n"
            )

            for index, job in enumerate(
                self.recommendations, start=1
            ):

                self.output.insert(
                    tk.END,
                    f"{index}. {job['title']}\n"
                )

                self.output.insert(
                    tk.END,
                    f"   Match: {job['match']}%\n"
                )

                self.output.insert(
                    tk.END,
                    f"   Skills: {job['skills']}\n"
                )

                self.output.insert(
                    tk.END,
                    f"   Description: {job['description']}\n\n"
                )

            if not self.recommendations:
                self.output.insert(
                    tk.END,
                    "No job recommendations found."
                )

            self.update_cards()

        except Exception as error:

            messagebox.showerror(
                "Job Error",
                str(error)
            )

                                                      

    def show_score(self):

        try:

            if not self.load_analysis():
                return

            score = self.analysis["score"]

            self.output.delete("1.0", tk.END)

            self.output.insert(
                tk.END,
                "========== RESUME SCORE ==========\n\n"
            )

            self.output.insert(
                tk.END,
                f"Your Resume Score: {score}/100\n\n"
            )

            if score >= 80:
                message = "Excellent! Your resume covers most checked sections."

            elif score >= 60:
                message = "Good! Some improvements can make your resume stronger."

            elif score >= 40:
                message = "Average! Try improving missing resume sections."

            else:
                message = "Needs Improvement! Add important resume information."

            self.output.insert(tk.END, message)

            self.update_cards()

        except Exception as error:

            messagebox.showerror("Error", str(error))

                                                          

    def show_tips(self):

        try:

            if not self.load_analysis():
                return

            self.output.delete("1.0", tk.END)

            self.output.insert(
                tk.END,
                "========== RESUME IMPROVEMENT TIPS ==========\n\n"
            )

            for index, tip in enumerate(
                self.analysis["tips"], start=1
            ):

                self.output.insert(
                    tk.END,
                    f"{index}. {tip}\n\n"
                )

            self.update_cards()

        except Exception as error:

            messagebox.showerror("Error", str(error))

                                                      

    def update_cards(self):

        self.score_value.config(
            text=f"{self.analysis['score']}/100"
        )

        self.skills_value.config(
            text=str(len(self.analysis["skills"]))
        )

        if self.recommendations is not None:
            self.jobs_value.config(
                text=str(len(self.recommendations))
            )

                                                     

    def reset_cards(self):

        self.score_value.config(text="--")
        self.skills_value.config(text="--")
        self.jobs_value.config(text="--")

                                                       

    def clear_results(self):

        self.resume_path = ""
        self.resume_text = ""
        self.analysis = None
        self.recommendations = None

        self.file_label.config(
            text="No resume selected",
            fg=ORANGE
        )

        self.output.delete("1.0", tk.END)

        self.output.insert(
            tk.END,
            "Results cleared successfully!\n\n"
            "Upload a new resume to start again."
        )

        self.reset_cards()

                                                     

if __name__ == "__main__":

    root = tk.Tk()

    app = ResumeAnalyzerApp(root)

    root.mainloop()