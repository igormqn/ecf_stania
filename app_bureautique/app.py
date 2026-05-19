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


# ─── Login window ────────────────────────────────────────────────────────────

def login_window():
    win = tk.Tk()
    win.title("Stania Bet — Commentator Login")
    win.geometry("380x250")
    win.resizable(False, False)
    win.configure(bg="#7ca5a6")

    tk.Label(win, text="Stania Bet", font=("Helvetica", 20, "bold"),
             bg="#7ca5a6", fg="white").pack(pady=20)
    tk.Label(win, text="Commentator Login", font=("Helvetica", 12),
             bg="#7ca5a6", fg="white").pack()

    frame = tk.Frame(win, bg="#7ca5a6")
    frame.pack(pady=10)

    tk.Label(frame, text="E-mail:", bg="#7ca5a6", fg="white").grid(row=0, column=0, sticky="e", padx=5, pady=5)
    email_var = tk.StringVar()
    tk.Entry(frame, textvariable=email_var, width=28).grid(row=0, column=1)

    tk.Label(frame, text="Password:", bg="#7ca5a6", fg="white").grid(row=1, column=0, sticky="e", padx=5, pady=5)
    pwd_var = tk.StringVar()
    tk.Entry(frame, textvariable=pwd_var, show="*", width=28).grid(row=1, column=1)

    def do_login():
        try:
            r = SESSION.post(f"{BASE_URL}/api/login/", json={
                "email": email_var.get().strip(),
                "password": pwd_var.get()
            }, timeout=5)
            if r.status_code == 200:
                win.destroy()
                main_window(r.json()["name"])
            else:
                messagebox.showerror("Login Failed", "Incorrect email or password.")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", f"Cannot reach server:\n{BASE_URL}")

    tk.Button(win, text="Login", command=do_login,
              bg="white", fg="#7ca5a6", font=("Helvetica", 11, "bold"),
              padx=20, pady=5).pack(pady=15)
    win.mainloop()


# ─── Main window ─────────────────────────────────────────────────────────────

def main_window(username):
    root = tk.Tk()
    root.title(f"Stania Bet — {username}")
    root.geometry("960x620")
    root.configure(bg="#f4f4f4")

    # Header
    header = tk.Frame(root, bg="#7ca5a6", height=60)
    header.pack(fill="x")
    tk.Label(header, text="Stania Bet  |  Desktop Application",
             font=("Helvetica", 16, "bold"), bg="#7ca5a6", fg="white").pack(side="left", padx=20, pady=10)
    tk.Label(header, text=f"Logged in as: {username}",
             font=("Helvetica", 11), bg="#7ca5a6", fg="white").pack(side="right", padx=20, pady=10)

    # Split layout
    paned = tk.PanedWindow(root, orient="horizontal", sashwidth=4)
    paned.pack(fill="both", expand=True)

    # ── Left panel: today's match list ──
    left = tk.Frame(paned, bg="#e8e8e8", width=300)
    paned.add(left)

    tk.Label(left, text=f"Today's Matches — {date.today().strftime('%d/%m/%Y')}",
             font=("Helvetica", 12, "bold"), bg="#e8e8e8").pack(pady=10, padx=10, anchor="w")

    lb_frame = tk.Frame(left, bg="#e8e8e8")
    lb_frame.pack(fill="both", expand=True, padx=5, pady=5)

    scrollbar = tk.Scrollbar(lb_frame)
    scrollbar.pack(side="right", fill="y")

    match_listbox = tk.Listbox(lb_frame, yscrollcommand=scrollbar.set,
                                font=("Helvetica", 10), selectbackground="#7ca5a6",
                                activestyle="none", cursor="hand2")
    match_listbox.pack(fill="both", expand=True)
    scrollbar.config(command=match_listbox.yview)

    tk.Button(left, text="↺ Refresh", bg="#7ca5a6", fg="white",
              command=lambda: load_matches()).pack(pady=8)

    # ── Right panel: match detail ──
    right = tk.Frame(paned, bg="white")
    paned.add(right)

    detail = tk.Frame(right, bg="white")
    detail.pack(fill="both", expand=True, padx=15, pady=10)

    title_lbl = tk.Label(detail, text="Select a match",
                          font=("Helvetica", 15, "bold"), bg="white", fg="#7ca5a6")
    title_lbl.pack(anchor="w")

    info_lbl = tk.Label(detail, text="", justify="left",
                         font=("Helvetica", 11), bg="white")
    info_lbl.pack(anchor="w", pady=5)

    # Score section
    score_frame = tk.LabelFrame(detail, text="Score", bg="white", font=("Helvetica", 11, "bold"))
    score_frame.pack(fill="x", pady=5)

    score_t1_var = tk.IntVar(value=0)
    score_t2_var = tk.IntVar(value=0)
    score_t1_lbl = tk.Label(score_frame, text="Team 1:", bg="white")
    score_t1_lbl.grid(row=0, column=0, padx=8, pady=4)
    tk.Spinbox(score_frame, from_=0, to=200, textvariable=score_t1_var, width=5).grid(row=0, column=1)
    score_t2_lbl = tk.Label(score_frame, text="Team 2:", bg="white")
    score_t2_lbl.grid(row=0, column=2, padx=8)
    tk.Spinbox(score_frame, from_=0, to=200, textvariable=score_t2_var, width=5).grid(row=0, column=3)

    # Commentary input
    comm_frame = tk.LabelFrame(detail, text="Add Commentary", bg="white", font=("Helvetica", 11, "bold"))
    comm_frame.pack(fill="x", pady=5)
    comm_text = tk.Text(comm_frame, height=3, font=("Helvetica", 10), wrap="word")
    comm_text.pack(fill="x", padx=5, pady=5)

    # Commentary history
    hist_frame = tk.LabelFrame(detail, text="Commentary & Score History",
                                bg="white", font=("Helvetica", 11, "bold"))
    hist_frame.pack(fill="both", expand=True, pady=5)
    hist_text = tk.Text(hist_frame, state="disabled", font=("Helvetica", 10),
                         bg="#fafafa", wrap="word")
    hist_text.pack(fill="both", expand=True, padx=5, pady=5)

    # Action buttons
    btn_frame = tk.Frame(detail, bg="white")
    btn_frame.pack(fill="x", pady=8)

    current_match = {"data": None}

    def btn_start():
        if not current_match["data"]:
            return
        mid = current_match["data"]["id"]
        if messagebox.askyesno("Start Match", "Start this match now?"):
            api_update_match(mid, {"action": "start"})
            refresh_detail(mid)
            load_matches()

    def btn_send_commentary():
        if not current_match["data"]:
            return
        mid = current_match["data"]["id"]
        txt = comm_text.get("1.0", "end").strip()
        if not txt:
            messagebox.showwarning("Warning", "Commentary is empty.")
            return
        payload = {
            "action": "add_commentary",
            "commentary": txt,
            "score_team1": score_t1_var.get(),
            "score_team2": score_t2_var.get(),
        }
        api_update_match(mid, payload)
        comm_text.delete("1.0", "end")
        refresh_detail(mid)

    def btn_close():
        if not current_match["data"]:
            return
        mid = current_match["data"]["id"]
        if messagebox.askyesno("Close Match", "Close this match and calculate winnings?"):
            api_update_match(mid, {"action": "close"})
            refresh_detail(mid)
            load_matches()

    tk.Button(btn_frame, text="▶ Start Match", bg="#457b9d", fg="white",
              font=("Helvetica", 10, "bold"), padx=10, command=btn_start).pack(side="left", padx=4)
    tk.Button(btn_frame, text="💬 Send Commentary", bg="#7ca5a6", fg="white",
              font=("Helvetica", 10), padx=10, command=btn_send_commentary).pack(side="left", padx=4)
    tk.Button(btn_frame, text="■ Close Match", bg="#e63946", fg="white",
              font=("Helvetica", 10, "bold"), padx=10, command=btn_close).pack(side="left", padx=4)

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
                    icon = {"Scheduled": "🕐", "Ongoing": "🟢", "Completed": "✅"}.get(m["status"], "")
                    match_listbox.insert("end",
                        f"{icon} {m['team1']} vs {m['team2']}  {m['start_time'][:5]}")
            else:
                messagebox.showerror("API Error", f"Status {r.status_code}")
        except requests.exceptions.ConnectionError:
            messagebox.showerror("Connection Error", f"Server unreachable:\n{BASE_URL}")

    def on_match_select(event):
        sel = match_listbox.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx < len(matches_cache):
            refresh_detail(matches_cache[idx]["id"])

    def refresh_detail(match_id):
        try:
            r = SESSION.get(f"{BASE_URL}/api/matches/{match_id}/", timeout=5)
            if r.status_code != 200:
                return
            m = r.json()
            current_match["data"] = m
            title_lbl.config(text=f"{m['team1']} vs {m['team2']}")
            status_map = {"Scheduled": "Upcoming", "Ongoing": "Ongoing", "Completed": "Completed"}
            info_lbl.config(text=(
                f"Date: {m['game_date']}   Start: {m['start_time'][:5]}   End: {m['end_time'][:5]}\n"
                f"Status: {status_map.get(m['status'], m['status'])}\n"
                f"Odds: {m['team1']} × {m['odds_team1']}   |   {m['team2']} × {m['odds_team2']}\n"
                f"Bets: {m['bets_team1_count']} on {m['team1']}  /  {m['bets_team2_count']} on {m['team2']}"
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
