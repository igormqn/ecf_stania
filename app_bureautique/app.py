"""
Desktop Application — Stania Bet (Commentator)
Communicates with the Django back-end via the REST API.
Run: python app.py
"""

import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import date

BASE_URL = "http://127.0.0.1:8000"
SESSION = requests.Session()

# ── Palette (mirrors website & Flutter app) ───────────────────────────────────
NAVY_900  = "#080F1E"
NAVY_800  = "#0D1729"
NAVY_700  = "#112035"
NAVY_600  = "#162840"
SURFACE   = "#111827"
BORDER    = "#1F2937"
GOLD_500  = "#F59E0B"
GOLD_400  = "#FBBF24"
CYAN_400  = "#22D3EE"
TEXT_PRI  = "#F1F5F9"
TEXT_SEC  = "#94A3B8"
GREEN     = "#4ADE80"
RED       = "#F87171"
ORANGE    = "#FB923C"


def _apply_ttk_styles():
    style = ttk.Style()
    style.theme_use("clam")

    style.configure(".",
        background=SURFACE,
        foreground=TEXT_PRI,
        fieldbackground=NAVY_700,
        bordercolor=BORDER,
        troughcolor=NAVY_900,
        selectbackground=GOLD_500,
        selectforeground=NAVY_900,
        font=("Segoe UI", 10),
    )
    style.configure("TFrame",    background=SURFACE)
    style.configure("TLabel",    background=SURFACE, foreground=TEXT_PRI, font=("Segoe UI", 10))
    style.configure("TEntry",    fieldbackground=NAVY_700, foreground=TEXT_PRI,
                    insertcolor=TEXT_PRI, bordercolor=BORDER, relief="flat")
    style.map("TEntry", bordercolor=[("focus", GOLD_500)])
    style.configure("TScrollbar", background=NAVY_700, troughcolor=NAVY_900,
                    arrowcolor=TEXT_SEC)

    style.configure("Gold.TButton",
        background=GOLD_500, foreground=NAVY_900,
        font=("Segoe UI", 10, "bold"), padding=(14, 6), relief="flat")
    style.map("Gold.TButton",
        background=[("active", GOLD_400), ("disabled", BORDER)],
        foreground=[("disabled", TEXT_SEC)])

    style.configure("Cyan.TButton",
        background=CYAN_400, foreground=NAVY_900,
        font=("Segoe UI", 10, "bold"), padding=(12, 6), relief="flat")
    style.map("Cyan.TButton", background=[("active", "#38BDF8")])

    style.configure("Red.TButton",
        background=RED, foreground=NAVY_900,
        font=("Segoe UI", 10, "bold"), padding=(12, 6), relief="flat")
    style.map("Red.TButton", background=[("active", "#FCA5A5")])

    style.configure("Header.TLabel",
        background=NAVY_800, foreground=TEXT_PRI,
        font=("Segoe UI", 16, "bold"))
    style.configure("Sub.TLabel",
        background=NAVY_800, foreground=TEXT_SEC,
        font=("Segoe UI", 10))

    style.configure("Section.TLabel",
        background=SURFACE, foreground=GOLD_400,
        font=("Segoe UI", 11, "bold"))
    style.configure("Title.TLabel",
        background=SURFACE, foreground=TEXT_PRI,
        font=("Segoe UI", 15, "bold"))
    style.configure("Info.TLabel",
        background=SURFACE, foreground=TEXT_SEC,
        font=("Segoe UI", 10))
    style.configure("Date.TLabel",
        background=NAVY_800, foreground=TEXT_SEC,
        font=("Segoe UI", 10))

    style.configure("Left.TFrame", background=NAVY_800)
    style.configure("Left.TLabel", background=NAVY_800, foreground=TEXT_PRI,
                    font=("Segoe UI", 11, "bold"))


# ─── Login window ────────────────────────────────────────────────────────────

def login_window():
    win = tk.Tk()
    win.title("Stania Bet — Commentator Login")
    win.geometry("400x300")
    win.resizable(False, False)
    win.configure(bg=NAVY_900)
    _apply_ttk_styles()

    # Title
    tk.Label(win, text="STANIA BET", font=("Segoe UI", 26, "bold"),
             bg=NAVY_900, fg=GOLD_400).pack(pady=(28, 0))
    tk.Label(win, text="Commentator Login", font=("Segoe UI", 11),
             bg=NAVY_900, fg=TEXT_SEC).pack(pady=(2, 20))

    # Card frame
    card = tk.Frame(win, bg=SURFACE, bd=0, highlightthickness=1,
                    highlightbackground=BORDER)
    card.pack(padx=40, fill="x")

    inner = tk.Frame(card, bg=SURFACE, padx=20, pady=18)
    inner.pack(fill="x")

    def row(label, var, show=""):
        tk.Label(inner, text=label, bg=SURFACE, fg=TEXT_SEC,
                 font=("Segoe UI", 10), anchor="w").pack(fill="x")
        e = tk.Entry(inner, textvariable=var, show=show,
                     bg=NAVY_700, fg=TEXT_PRI, insertbackground=TEXT_PRI,
                     relief="flat", bd=0, highlightthickness=1,
                     highlightbackground=BORDER, highlightcolor=GOLD_500,
                     font=("Segoe UI", 10))
        e.pack(fill="x", ipady=6, pady=(2, 10))
        return e

    email_var = tk.StringVar()
    pwd_var   = tk.StringVar()
    row("E-mail", email_var)
    pwd_entry = row("Password", pwd_var, show="*")

    error_lbl = tk.Label(inner, text="", bg=SURFACE, fg=RED,
                         font=("Segoe UI", 9), anchor="w")
    error_lbl.pack(fill="x")

    def do_login(event=None):
        error_lbl.config(text="")
        try:
            r = SESSION.post(f"{BASE_URL}/api/login/", json={
                "email": email_var.get().strip(),
                "password": pwd_var.get()
            }, timeout=5)
            if r.status_code == 200:
                win.destroy()
                main_window(r.json()["name"])
            else:
                error_lbl.config(text="Incorrect email or password.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", f"Cannot reach server:\n{BASE_URL}")

    pwd_entry.bind("<Return>", do_login)

    btn = tk.Button(inner, text="Sign In", command=do_login,
                    bg=GOLD_500, fg=NAVY_900, activebackground=GOLD_400,
                    activeforeground=NAVY_900, font=("Segoe UI", 11, "bold"),
                    relief="flat", cursor="hand2", pady=8)
    btn.pack(fill="x", pady=(4, 0))

    win.mainloop()


# ─── Main window ─────────────────────────────────────────────────────────────

def main_window(username):
    root = tk.Tk()
    root.title(f"Stania Bet — {username}")
    root.geometry("1060x660")
    root.configure(bg=NAVY_900)

    # ── Header ──
    header = tk.Frame(root, bg=NAVY_800, height=56)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(header, text="STANIA BET",
             font=("Segoe UI", 17, "bold"), bg=NAVY_800, fg=GOLD_400).pack(
             side="left", padx=20, pady=8)
    tk.Label(header, text="Desktop Application",
             font=("Segoe UI", 11), bg=NAVY_800, fg=TEXT_SEC).pack(
             side="left", pady=8)
    tk.Label(header, text=f"Logged in as: {username}",
             font=("Segoe UI", 10), bg=NAVY_800, fg=TEXT_SEC).pack(
             side="right", padx=20)

    # ── Split layout ──
    paned = tk.PanedWindow(root, orient="horizontal", sashwidth=4,
                           bg=BORDER, sashrelief="flat")
    paned.pack(fill="both", expand=True)

    # ── Left panel: match list ──
    left = tk.Frame(paned, bg=NAVY_800, width=280)
    paned.add(left)

    hdr_left = tk.Frame(left, bg=NAVY_800, padx=12, pady=12)
    hdr_left.pack(fill="x")
    tk.Label(hdr_left, text=f"Today's Matches",
             font=("Segoe UI", 12, "bold"), bg=NAVY_800, fg=TEXT_PRI).pack(anchor="w")
    tk.Label(hdr_left, text=date.today().strftime("%A, %d %B %Y"),
             font=("Segoe UI", 9), bg=NAVY_800, fg=TEXT_SEC).pack(anchor="w")

    # Separator
    tk.Frame(left, bg=BORDER, height=1).pack(fill="x")

    lb_wrap = tk.Frame(left, bg=NAVY_800, padx=8, pady=8)
    lb_wrap.pack(fill="both", expand=True)

    scrollbar = tk.Scrollbar(lb_wrap, bg=NAVY_700, troughcolor=NAVY_900,
                             activebackground=GOLD_500, relief="flat", bd=0)
    scrollbar.pack(side="right", fill="y")

    match_listbox = tk.Listbox(
        lb_wrap,
        yscrollcommand=scrollbar.set,
        font=("Segoe UI", 10),
        bg=NAVY_800, fg=TEXT_PRI,
        selectbackground=GOLD_500, selectforeground=NAVY_900,
        activestyle="none", cursor="hand2",
        relief="flat", bd=0, highlightthickness=0,
    )
    match_listbox.pack(fill="both", expand=True)
    scrollbar.config(command=match_listbox.yview)

    tk.Frame(left, bg=BORDER, height=1).pack(fill="x")
    btn_refresh_wrap = tk.Frame(left, bg=NAVY_800, pady=10)
    btn_refresh_wrap.pack(fill="x")
    refresh_btn = tk.Button(
        btn_refresh_wrap, text="↺  Refresh",
        bg=NAVY_700, fg=CYAN_400, activebackground=BORDER, activeforeground=CYAN_400,
        font=("Segoe UI", 10, "bold"), relief="flat", cursor="hand2",
        pady=7, command=lambda: load_matches()
    )
    refresh_btn.pack(fill="x", padx=10)

    # ── Right panel: detail ──
    right = tk.Frame(paned, bg=SURFACE)
    paned.add(right)

    detail = tk.Frame(right, bg=SURFACE, padx=20, pady=14)
    detail.pack(fill="both", expand=True)

    title_lbl = tk.Label(detail, text="Select a match on the left",
                         font=("Segoe UI", 16, "bold"), bg=SURFACE, fg=TEXT_SEC)
    title_lbl.pack(anchor="w")

    status_lbl = tk.Label(detail, text="", font=("Segoe UI", 10, "bold"),
                          bg=SURFACE, fg=CYAN_400)
    status_lbl.pack(anchor="w", pady=(2, 0))

    info_lbl = tk.Label(detail, text="", justify="left",
                        font=("Segoe UI", 10), bg=SURFACE, fg=TEXT_SEC)
    info_lbl.pack(anchor="w", pady=(2, 10))

    tk.Frame(detail, bg=BORDER, height=1).pack(fill="x", pady=(0, 10))

    # Score section
    score_card = tk.Frame(detail, bg=NAVY_700, padx=14, pady=10,
                          highlightthickness=1, highlightbackground=BORDER)
    score_card.pack(fill="x", pady=(0, 10))

    tk.Label(score_card, text="SCORE", font=("Segoe UI", 9, "bold"),
             bg=NAVY_700, fg=TEXT_SEC).grid(row=0, column=0, columnspan=4, pady=(0, 8))

    score_t1_var = tk.IntVar(value=0)
    score_t2_var = tk.IntVar(value=0)

    score_t1_lbl = tk.Label(score_card, text="Team 1:", bg=NAVY_700, fg=TEXT_PRI,
                             font=("Segoe UI", 10))
    score_t1_lbl.grid(row=1, column=0, padx=(0, 6), sticky="e")

    tk.Spinbox(score_card, from_=0, to=200, textvariable=score_t1_var, width=5,
               bg=NAVY_900, fg=GOLD_400, buttonbackground=NAVY_600,
               relief="flat", font=("Segoe UI", 11, "bold"),
               insertbackground=TEXT_PRI).grid(row=1, column=1, padx=4)

    tk.Label(score_card, text="—", bg=NAVY_700, fg=GOLD_400,
             font=("Segoe UI", 18, "bold")).grid(row=1, column=2, padx=10)

    score_t2_lbl = tk.Label(score_card, text="Team 2:", bg=NAVY_700, fg=TEXT_PRI,
                             font=("Segoe UI", 10))
    score_t2_lbl.grid(row=1, column=3, padx=(0, 6), sticky="e")

    tk.Spinbox(score_card, from_=0, to=200, textvariable=score_t2_var, width=5,
               bg=NAVY_900, fg=GOLD_400, buttonbackground=NAVY_600,
               relief="flat", font=("Segoe UI", 11, "bold"),
               insertbackground=TEXT_PRI).grid(row=1, column=4, padx=4)

    # Commentary input
    tk.Label(detail, text="Add Commentary", font=("Segoe UI", 11, "bold"),
             bg=SURFACE, fg=GOLD_400).pack(anchor="w", pady=(0, 4))

    comm_text = tk.Text(
        detail, height=3, font=("Segoe UI", 10), wrap="word",
        bg=NAVY_700, fg=TEXT_PRI, insertbackground=TEXT_PRI,
        relief="flat", bd=0, highlightthickness=1, highlightbackground=BORDER,
        padx=8, pady=6,
    )
    comm_text.pack(fill="x", pady=(0, 10))

    # Action buttons
    btn_frame = tk.Frame(detail, bg=SURFACE)
    btn_frame.pack(fill="x", pady=(0, 12))

    current_match = {"data": None}

    def _btn(parent, text, color, active_color, cmd):
        b = tk.Button(parent, text=text, command=cmd,
                      bg=color, fg=NAVY_900, activebackground=active_color,
                      activeforeground=NAVY_900,
                      font=("Segoe UI", 10, "bold"), relief="flat",
                      cursor="hand2", padx=14, pady=7)
        b.pack(side="left", padx=(0, 8))
        return b

    def btn_start():
        if not current_match["data"]: return
        mid = current_match["data"]["id"]
        if messagebox.askyesno("Start Match", "Start this match now?"):
            api_update_match(mid, {"action": "start"})
            refresh_detail(mid)
            load_matches()

    def btn_send_commentary():
        if not current_match["data"]: return
        mid = current_match["data"]["id"]
        txt = comm_text.get("1.0", "end").strip()
        if not txt:
            messagebox.showwarning("Warning", "Commentary is empty.")
            return
        api_update_match(mid, {
            "action": "add_commentary",
            "commentary": txt,
            "score_team1": score_t1_var.get(),
            "score_team2": score_t2_var.get(),
        })
        comm_text.delete("1.0", "end")
        refresh_detail(mid)

    def btn_close():
        if not current_match["data"]: return
        mid = current_match["data"]["id"]
        if messagebox.askyesno("Close Match", "Close this match and calculate winnings?"):
            api_update_match(mid, {"action": "close"})
            refresh_detail(mid)
            load_matches()

    _btn(btn_frame, "▶  Start Match",       "#457B9D", "#5A9ABF", btn_start)
    _btn(btn_frame, "💬  Send Commentary",  GOLD_500,  GOLD_400,  btn_send_commentary)
    _btn(btn_frame, "■  Close Match",       RED,       "#FCA5A5", btn_close)

    # Commentary history
    tk.Frame(detail, bg=BORDER, height=1).pack(fill="x", pady=(0, 8))
    tk.Label(detail, text="Commentary & Score History", font=("Segoe UI", 11, "bold"),
             bg=SURFACE, fg=GOLD_400).pack(anchor="w", pady=(0, 4))

    hist_wrap = tk.Frame(detail, bg=NAVY_700, highlightthickness=1,
                         highlightbackground=BORDER)
    hist_wrap.pack(fill="both", expand=True)

    hist_scroll = tk.Scrollbar(hist_wrap, bg=NAVY_700, troughcolor=NAVY_900,
                               activebackground=GOLD_500, relief="flat", bd=0)
    hist_scroll.pack(side="right", fill="y")

    hist_text = tk.Text(
        hist_wrap, state="disabled", font=("Segoe UI", 10), wrap="word",
        bg=NAVY_700, fg=TEXT_SEC, relief="flat", bd=0, highlightthickness=0,
        padx=10, pady=8, yscrollcommand=hist_scroll.set,
    )
    hist_text.pack(fill="both", expand=True)
    hist_scroll.config(command=hist_text.yview)

    # ── Data loading ──
    matches_cache = []

    def load_matches():
        match_listbox.delete(0, "end")
        matches_cache.clear()
        try:
            r = SESSION.get(f"{BASE_URL}/api/matches/today/", timeout=5)
            if r.status_code == 200:
                for m in r.json():
                    matches_cache.append(m)
                    icon = {"Scheduled": "○", "Ongoing": "●", "Completed": "✓"}.get(m["status"], "")
                    match_listbox.insert("end",
                        f"  {icon}  {m['team1']} vs {m['team2']}   {m['start_time'][:5]}")
                    if m["status"] == "Ongoing":
                        match_listbox.itemconfig(
                            match_listbox.size() - 1, fg=ORANGE)
                    elif m["status"] == "Completed":
                        match_listbox.itemconfig(
                            match_listbox.size() - 1, fg=TEXT_SEC)
            else:
                messagebox.showerror("API Error", f"Status {r.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", f"Server unreachable:\n{BASE_URL}")

    def on_match_select(event):
        sel = match_listbox.curselection()
        if not sel: return
        idx = sel[0]
        if idx < len(matches_cache):
            refresh_detail(matches_cache[idx]["id"])

    def refresh_detail(match_id):
        try:
            r = SESSION.get(f"{BASE_URL}/api/matches/{match_id}/", timeout=5)
            if r.status_code != 200: return
            m = r.json()
            current_match["data"] = m

            title_lbl.config(text=f"{m['team1']}  vs  {m['team2']}", fg=TEXT_PRI)

            status_colors = {"Scheduled": CYAN_400, "Ongoing": ORANGE, "Completed": TEXT_SEC}
            status_labels = {"Scheduled": "● Upcoming", "Ongoing": "● Ongoing", "Completed": "✓ Completed"}
            status_lbl.config(
                text=status_labels.get(m["status"], m["status"]),
                fg=status_colors.get(m["status"], TEXT_SEC),
            )

            info_lbl.config(text=(
                f"Date: {m['game_date']}     Start: {m['start_time'][:5]}     End: {m['end_time'][:5]}\n"
                f"Odds:  {m['team1']} × {m['odds_team1']}   |   {m['team2']} × {m['odds_team2']}\n"
                f"Bets:  {m['bets_team1_count']} on {m['team1']}   /   {m['bets_team2_count']} on {m['team2']}"
            ))

            score_t1_lbl.config(text=f"{m['team1']}:")
            score_t2_lbl.config(text=f"{m['team2']}:")
            score_t1_var.set(m["score_team1"])
            score_t2_var.set(m["score_team2"])

            hist_text.config(state="normal")
            hist_text.delete("1.0", "end")
            hist_text.insert("end", m["commentary"] if m["commentary"] else "(no commentary yet)")
            hist_text.config(state="disabled")
        except requests.exceptions.ConnectionError:
            pass

    match_listbox.bind("<<ListboxSelect>>", on_match_select)
    load_matches()
    root.mainloop()


# ─── API helper ──────────────────────────────────────────────────────────────

def api_update_match(match_id, payload):
    try:
        r = SESSION.post(
            f"{BASE_URL}/api/matches/{match_id}/update/",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=5,
        )
        if r.status_code != 200:
            messagebox.showerror("API Error", f"Code {r.status_code}\n{r.text[:300]}")
    except requests.exceptions.ConnectionError:
        messagebox.showerror("Connection Error", f"Server unreachable: {BASE_URL}")


if __name__ == "__main__":
    login_window()
