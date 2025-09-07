# RUET CampusConnect

**RUET CampusConnect** is a centralized communication and collaboration platform tailored for the vibrant community of RUET. Our university is home to a diverse range of clubs and organizations — from ASSR to PSR, RUETDC, and many others including zilla-based associations. While most of these currently rely on platforms like Facebook and Messenger, these tools often lead to distractions such as reels and videos.

**CampusConnect** aims to eliminate this friction by offering a focused, clutter-free, and productive environment for communication within and across student groups, faculty, and staff. Think of it as a Reddit-style platform designed exclusively for RUET — but better suited to our academic and organizational needs.

---

## Vision

To build a collaborative digital space where RUETians can:

- Discuss ideas and activities,
- Stay updated with club announcements,
- Participate in event planning,
- Share multimedia and academic resources,
- Engage in meaningful dialogue — all in one place.

---

## Key Features

- 🔐 **User Authentication** — Sign up, log in, manage profiles
- 🧵 **Threads for Clubs & Orgs** — Post, comment, and reply
- 👍 **Interactive Tools** — Upvote, downvote, and save posts
- 🔍 **Smooth UX** — Search, sort, and filter content easily
- 📅 **Multimedia & Events** — Images, videos, calendar integration
- 🛡 **Moderation Tools** — Report, block, and content removal
- 💬 **Messaging** — Direct and group chat functionality

---

## 🛠 Tech Stack

- 🐍 **Python**
- 🌐 **Django** — Backend framework
- ⚡ **HTMX** — For dynamic frontend interactions
- 🎨 **Tailwind CSS** — Utility-first styling
- 🧩 **Alpine.js** — Lightweight frontend logic

---

## 📁 Project Structure (Modular)

```text
ruetconnect/
├── apps/
│   ├── campus/         # Campus homepage and core pages
│   ├── posts/          # Forum posts and threads
│   ├── comments/       # Nested comments and replies
│   ├── threads/        # Topic-based discussions
│   ├── users/          # Profiles, login, registration
│   └── votes/          # Upvotes, downvotes
├── config/             # Project settings and routing
├── shared/             # Utilities, constants, mixins
├── templates/          # Base and shared HTML templates
├── static/             # Static files (JS, CSS, images)
├── media/              # Uploaded content
├── pyproject.toml      # Dependency management
└── manage.py
```

---

## 🤝 Contributing

Want to help build RUET's future communication hub? Contributions are welcome! Feel free to fork the repo, open issues, or submit pull requests.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 💡 Acknowledgments

Built with 💙 for the RUET community.
