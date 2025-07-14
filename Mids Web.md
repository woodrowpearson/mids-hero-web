# **Mids Reborn Repository Analysis and Rewrite Plan**

## **Repository Structure and Overview**

**Mids Reborn (MIDS-WEB)** is an open-source character build planner for *City of Heroes*, implemented as a Windows Forms desktop application targeting .NET 8\. The repository is organized into multiple projects that together form the application:

* **MidsReborn (Main App):** The primary C\# WinForms application (`MidsReborn` directory). This contains the UI forms (e.g. `frmMain`, various dialogs under `Forms/`), core logic, and data handling. The app’s entry point is `Program.cs`, which initializes the updater and launches the WinForms context. The main form (`MainForm`) provides the GUI for designing character builds (selecting archetypes, powers, enhancements, etc.). The UI uses WinForms controls and some custom controls (in `Forms/Controls` and `UIv2/Controls`), with styling enhancements (e.g. integration of WebView2 for the splash screen animation).

* **Data Files:** Under `MidsReborn/Data/`, the repository includes game database files for different server “realms” (e.g. **Homecoming**, **Rebirth**). These files (with extensions `.mhd` or `.json`) encode all game data: powers, archetypes, enhancements, recipes, etc. For example, the Homecoming realm data includes files like `I12.mhd` (main powers database), `EnhDB.mhd` (enhancements database), `Recipe.mhd` (crafting recipes), `Salvage.mhd` (salvage items), `Origins.mhd` (origin types), `AttribMod.mhd` (attribute modifiers), and others. Image assets for powers and enhancements are under `Data/<Realm>/Images`. The app by default uses the **Homecoming** database (the largest community server) as the “Current Database,” though it can switch to others (like Rebirth) via the options. Each database is versioned (e.g. Homecoming *2025.7.1111* corresponds to a specific game data version).

* **Core Logic & Models:** The `MidsReborn/Core` folder contains the logic for loading and managing the data, as well as definitions of data models. The **data model** is defined in subnamespaces like `Core.Base.Data_Classes` and `Core.Base.Master_Classes`. These include classes for Archetypes, Powersets, Powers, Enhancements, etc., often stored in a singleton `Database` instance in memory (accessible via `DatabaseAPI.Database`). The app loads all data on startup into these structures for fast in-memory access. For example, the `Database.Classes` array holds all Archetype definitions, `Database.Powersets` all powerset definitions, and so on. The data classes are linked by numeric IDs and indexes (the code performs a matching process after load to link references). The `MidsReborn.Core.DatabaseAPI` static class provides high-level operations on the database: it handles loading all the data files, performing lookups by ID or name, and providing utility functions for the rest of the app.

* **Bootstrapper Updater (MRBBootstrap):** A separate component responsible for updates and patching. This is a *launcher/updater* program, partly written in C++ (`MRBBootstrap` folder with `Downloader.cpp`, `PatchManager.cpp`, etc.) and partly in C\# (`MRB_Bootstrap` folder for .NET bootstrap logic). The bootstrapper’s job is to check for updates to the main app or the game database and apply patches before launching the main WinForms app. On startup, `MidsReborn.Program` calls `StrapUpdater.Run()` which handles any just-downloaded updates (renaming files, etc.), then launches the main app context. The bootstrapper itself runs as a separate process (`MRBBootstrap.exe`) when needed – for example, if an update is available, the main app may invoke the bootstrapper to download and install the update. The C++ side of the bootstrapper manages HTTP downloads (using WinHTTP) and file patching, while the C\# side (with a hidden WinForms UI) coordinates user prompts and logs.

* **Logging and Utilities:** The repository uses **Serilog** for logging. The `MRBLogging` project provides a simple logger wrapper that tags logs with a component name. Logs are written to files (e.g. `Logs/bootstrapper.log` for the updater, and likely `Logs/mids.log` for the main app) and to console for debug. Various utility classes exist (in `Core.Utils`, `Core.Base.Extensions`, etc.) to support tasks like serialization, custom UI drawing, and constants (e.g. `Consts.cs` contains an HTML template for the splash screen WebView).

In summary, the repository’s high-level structure has a **Windows Forms UI layer**, a **core logic layer** that loads/manages game data, a set of **data files** representing the game content, and an **external updater utility** for maintaining up-to-date data and application code. This separation allows the main app to remain lightweight and focused on data presentation and editing, while the bootstrapper handles self-update functionality.

## **Technical Architecture Breakdown**

The Mids Reborn application can be viewed in layered components: **User Interface**, **Application Logic/Controllers**, **Data Model & Storage**, and **Update Mechanism** – all working together to provide the functionality of a character planner.

* **User Interface (WinForms):** The UI is built with traditional WinForms, with an emphasis on presenting complex data in a user-friendly way. The main window (`MainForm`) contains controls for selecting an Archetype (character class), primary and secondary power sets, pool powers, incarnate abilities, enhancements slots, etc. For instance, on load, the app populates dropdowns for Archetypes and Origins using the loaded `Database` content. When the user picks an Archetype from the combo box, the UI dynamically updates the available powers in the primary/secondary power set lists by binding to the selected Archetype’s data. The forms directory includes various other forms: e.g. `frmTeam` for team composition, forms under `OptionsMenuItems` for settings and data editing (like `frmServerData` to edit server-specific constants), and `WindowMenuItems` for additional info windows (set details, power info, etc.).

   The UI logic is mostly event-driven (button clicks, combo selection events update the model). There is a splash screen form (`Loader`) that appears on startup to show a loading animation and status messages. Notably, the splash uses a **WebView2** control to display an HTML/CSS animated loading screen (with a custom loading GIF). Once data loading is complete, the splash closes and the main form is shown. The UI uses double-buffering and some custom rendering (see `UIv2` controls and use of Win32 APIs for window theming), giving it a more modern feel despite being WinForms.

* **Application Logic & Controllers:** The core controller that orchestrates application startup and data loading is the `MainModule.MidsController` class. This static class contains methods to initialize or switch databases and to load all data on startup. On first run, if no database is selected, it auto-selects the default (Homecoming) database path and saves it to the config. The `LoadData` routine then sequentially loads each piece of game data, updating the splash screen text via an `IMessenger` interface (implemented by the Loader form) to inform the user of progress. The loading sequence is roughly:

  * **Config & Overrides:** Load user config (`appSettings.json`) and any override settings.

  * **Server Data:** Load server-specific constants (e.g. base movement speeds, max enhancement slots, incarnate availability) via `DatabaseAPI.LoadServerData`. This reads the **Server Data** file (`SData.json` if present, otherwise falls back to `SData.mhd`). These values (like base run speed, whether inherent slotting is enabled, etc.) populate the `ServerData` singleton. For example, Homecoming’s defaults are base accuracy 75%, certain incarnate slots disabled by default, max enhancement slots \= 67, etc., whereas another server like Rebirth might have different values (Rebirth’s `SData.json` sets max slots 72 and enables an extra incarnate “Genesis”). The server data also contains the URL for that server’s update manifest (e.g. Rebirth’s manifest URL is stored here).

  * **Main Game Data:** Load all the binary `.mhd` files for the selected realm. This includes:

    * **Leveling tables** (`NLevels.mhd`, `RLevels.mhd`): XP curves or level-up data (for “Normal” and “Incarnate/Prestige” leveling, presumably).

    * **Powers Database** (`I12.mhd`): The primary dataset of powers. This file contains definitions of all archetypes, powersets, and powers. It’s loaded via `DatabaseAPI.LoadMainDatabase` which reads the binary format. The file begins with a header string `"Mids Reborn Powers Database"` for validation, followed by version info and then lists of Archetypes, Powersets, Powers, etc. Each entry is stored as an object (Archetype, Powerset, Power classes) in the in-memory `Database` singleton. After loading, the code calls `DatabaseAPI.MatchAllIDs()` to resolve cross-references (linking powers to powersets, etc.) and `AssignSetBonusIndexes()`/`AssignRecipeIDs()` to finalize indexes.

    * **Mathematical constants** (`Maths.mhd`): Likely tables of formula constants or curves (e.g. how enhancements combine, diminishing returns, etc. needed for calculations).

    * **Global Chance Modifiers** (`GlobalMods.mhd`): Definitions for global proc chances or effects.

    * **Enhancement data**:

      * `EClasses.mhd` defines enhancement categories/classes.

      * `EnhDB.mhd` lists all enhancements (their bonuses, levels, etc.).

      * `AttribMod.mhd` and `TypeGrades.json` provide additional data for enhancement effects and set types/tiers.

    * **Inventories**:

      * `Salvage.mhd` lists crafting salvage items.

      * `Recipe.mhd` lists crafting recipes (which consume salvage).

      * `Compare.mhd` and `BBCode.mhd` are used for comparing builds and generating forum export text.

    * **Replacement Tables**: `PowersReplTable.mhd` and `CrypticPowerNames.mhd` are lookup tables for handling changes in power naming (used when loading older saved builds – e.g. replacing obsolete power IDs with new ones). These are loaded last if present.

    * **Images:** Although not “loaded” in the same way, the application also has an image pack for icons (powers, enhancements, etc.) under the Images folders. After data load, the app calls a routine to load graphics (likely reading all icon PNGs into memory or ensuring they are accessible).

* Throughout this process, if any critical data file fails to load or is missing, the application will show an error and exit. On success, `IsAppInitialized` is set true and the main UI becomes fully functional with all game data in memory.

* **Data Model:** Internally, the data is structured into classes reflecting game concepts. For example, there is an `Archetype` class (with fields like name, allowed primary/secondary sets, hit point modifiers, etc.), a `Powerset` class (list of Powers, grouping, archetype affinity), a `Power` class (with attributes like damage, recharge, buffs, etc.), and similar classes for Enhancements, Salvage, Recipes. Many of these are generated from the binary files. The code uses arrays and indexes for performance (e.g., `Database.Power[index]` gives a specific power, and powers reference enhancements by ID, etc.). The **character build** in progress is represented by a `clsToon` or `clsToonX` object (which holds the selected archetype, chosen powers, slots allocated, etc.). This object is what the UI modifies as the user builds their character, and it’s part of `MidsContext` (a static context holding global state like the current Character, the Config, and the loaded Database). The app can save and load builds to disk (in a "Hero & Villain Builds" folder in user documents) – likely in a custom format or JSON, though the repository hints at compressed save formats (strings like `"MRBz"` and `"ToonDataVersion"` appear in `Files.Headers.Save` constants indicating support for reading old Mids’ save files and the new format).

* **Configuration and Extensibility:** The app stores user preferences in a JSON config (`appSettings.json`) which tracks things like last used database, window size, etc. There is also support for *multiple databases*. By default, two are included (Homecoming and Rebirth), but users can potentially add others. The method `DatabaseAPI.GetInstalledDatabases()` scans `Data/` subfolders for available sets. On first run, if multiple are present, it would allow selection (the code suggests a dialog for database selection, though in current version it auto-picks the first non-“Generic” database). This architecture means the core logic is decoupled from any specific server’s data – new data sets can be dropped in as additional folders, and the app logic will handle them as long as they follow the expected format.

* **Update Mechanism:** Mids Reborn includes a robust self-update system. The application checks for updates to both the **application** and the **database** via manifests on remote servers. Specifically, the main update manifest is hosted by the Mids team (at **`updates.midsreborn.com`**). On startup or when the user triggers “Check for Updates,” the app will fetch `update_manifest.json` from the Mids server. This JSON manifest contains a list of available updates (each with a type: Application or Database, a name, version, and file URL). The app then compares the versions against the current app version and current database version in use.

  * For the **Homecoming database**, the primary manifest from the MidsReborn server includes its updates. (Homecoming is treated as the default, so no separate external manifest is needed – the code skips any external fetch if the active DB is "Homecoming".) In practice, the Mids team coordinates with the Homecoming developers to update this data; when Homecoming releases a new game version (e.g. 2025.7.1111), an updated data file (or patch) is made available on the Mids update server, and the manifest entry for "Homecoming" database is bumped to that version.

  * For **other servers** (e.g. Rebirth), the app expects an external manifest provided by that server’s community. For example, Rebirth’s `SData.json` sets its manifest URL to an XML file on Rebirth’s site. If the current database is not Homecoming, the updater will fetch the external manifest from the URL specified (unless none is configured). This allows community-run servers to maintain their own update info. The app is backward-compatible with older XML-based manifests (though it will warn if an XML manifest is used, encouraging a JSON update feed).

  * When an update is detected, the main app does not directly apply it (since it can’t overwrite files while running). Instead, it invokes the **bootstrapper (MRBBootstrap.exe)** in either “patch” mode or “rollback” mode with a manifest file. The bootstrapper is designed to run, present a minimalist GUI (a Modern UI window with progress bar), download the required patch files, validate them (via hashes), apply the updates (replacing or patching files in the install directory), and then restart the main application. The bootstrapper uses classes like `PatchFlowManager` and `PatchInstaller` to orchestrate this process. It can handle both app binary updates (replacing the .exe, .dll files) as well as database updates (downloading new .mhd/.json data files). The bootstrap logic includes safety measures like backing up current files, and the `StrapUpdater` in the main app will clean up any temporary files on next launch.

* In essence, the architecture ensures that the **game data stays current** by fetching updates over HTTP and applying them automatically, whether those updates originate from the MidsReborn team or partner servers. This remote-fetch logic is crucial, since the Homecoming database is **not hardcoded** in the app but rather kept up-to-date by downloading the latest version from a server when available. (During normal runs, the app uses the local copy of the database files in `Data\Homecoming\...`; the update system is what replaces those files when a new version comes out.)

* **Platform Considerations:** As a WinForms/.NET app, Mids Reborn currently runs on Windows (with unofficial support via Wine on Linux/Mac). It packages all data files with the installer, and updates are delivered via the mechanisms described. Because it’s a traditional desktop app, it stores everything locally (including user-created build files and downloaded databases) on the user’s machine, and the processing (build calculations, etc.) is all done in the local process.

**Summary of Current Architecture:** The Mids Reborn repo implements a classic thick-client design: a local UI and logic that loads game **data** from local storage, allows the user to manipulate that data (create a character build), and periodically updates the data/app by pulling from the internet. The codebase is organized into clear layers (UI forms, core logic, data definitions, updater) but all within a single application runtime. This provides a foundation to now envision a modern web-based rewrite, where responsibilities would be split between a backend server (for data and logic) and a frontend web UI.

## **Modern Web-Based Rewrite – Proposed Architecture**

To rewrite Mids Reborn as a **web-based application**, we will transition from a monolithic desktop app to a **client–server architecture** with a web frontend and a service-oriented backend. The goal is to maintain full *feature parity* with the existing application (all current functionalities and data), while improving the architecture for modern web standards, performance, and maintainability. Below is a high-level design for the new system:

* **Frontend:** A single-page web application (SPA) built with **React** (per your preference). This will be the primary user interface, running in the browser. The React app will replicate and improve upon the current UI/UX:

  * It will provide interactive components for selecting archetypes, power sets, and enhancements, similar to the WinForms UI. We can leverage modern UI libraries (e.g. Material-UI or Ant Design) to create dynamic dropdowns, drag-and-drop enhancement slotting, responsive layouts, etc.

  * The state management (using React state or a state library like Redux) will hold the current “build” data (selected powers, slots, etc.), analogous to the `clsToon` object in the original. As the user makes changes, calculations (like totals for powers, defense values, etc.) can be updated live on the client for responsiveness.

  * The frontend will communicate with the backend via RESTful API calls (or GraphQL if desired, though REST is straightforward for our use case) to fetch game data and possibly to offload complex calculations.

  * **Visualization & UX improvements:** The web app can improve on the original UX by offering tooltips, search/filter for powers or sets, and possibly real-time collaboration (like sharing a build via link). Initially, we will focus on matching the existing features, but the web platform will make it easier to add such enhancements over time.

* **Backend:** A server-side application in Python, running on an ASGI server (like **Uvicorn**). We will use modern Python web frameworks – likely **FastAPI** for the core API due to its performance and straightforward design, and possibly **Django** for certain components such as an admin interface or ORM if needed. The backend will handle:

  * **Data storage and management:** The game data (formerly in .mhd files) will be stored in a **PostgreSQL database**. We will design a relational schema that mirrors the data model:

    * Tables for Archetypes, Powersets, Powers, Enhancements, etc., with foreign keys to represent relationships (e.g. Powersets belong to an Archetype, Powers belong to a Powerset, Enhancement bonuses link to Powers or Archetypes where applicable, etc.).

    * This structured schema allows using SQL for queries (e.g. find all powers of a certain type, or all enhancements usable by a power) and ensures data integrity.

    * An ORM (Object-Relational Mapper) like **SQLAlchemy** or Django’s ORM will be used to map these tables to Python classes. This is analogous to the in-memory `Database` classes but backed by a real database. The ORM will simplify loading the data and performing updates when new game versions arrive.

  * **Business logic and APIs:** The server will expose endpoints for the frontend. Key API endpoints include:

    * **Data retrieval**: endpoints to fetch the list of archetypes, the powersets for a given archetype, the powers in a powerset, enhancements, etc. For example, `GET /api/archetypes` returns all archetypes, `GET /api/archetypes/{id}/powersets` returns that archetype’s power sets. These allow the React app to load initial data and populate dropdowns.

    * **Build calculations**: While much of the selection process can be handled on the client, certain calculations (like final attribute totals, damage outputs, etc.) could be done on the backend for accuracy. We can provide an endpoint where the frontend sends a representation of the current build (e.g. selected powers and slots) and the backend responds with computed stats (mimicking what the original app calculates when you toggle enhancements or powers). This ensures the complex math (which might involve formulas for diminishing returns, set bonuses, etc.) is centralized and consistent. Alternatively, these calculations could also be implemented in JavaScript to update instantly in the UI – we have flexibility here. Initially, we might implement simpler calculations on the client for responsiveness, and gradually move authoritative calculations to the server as needed.

    * **Persistence**: endpoints for saving and loading builds. Unlike the desktop version which saved to local files, the web app can save builds to the database (if we implement user accounts) or allow export/import as files for offline sharing. For an MVP, we might allow downloading a build as a JSON or text (comparable to the .mxd or .xml save format) and loading from such a file. Long-term, having user login and cloud-saved builds would be a great feature (optional in MVP).

    * **Update checks**: The backend will also handle fetching the latest game data updates from remote sources (similar to the original update mechanism, but now as a server concern). We can create an admin-only endpoint or a scheduled job on the server to periodically check Homecoming’s data version. For instance, a background task could weekly request the Mids Reborn update manifest or Homecoming’s data feed. If a new version (e.g. *2025.7.1215*) is available, the server can download the new data (perhaps the Mids team provides a data dump or patch file). The server would then update the PostgreSQL records with the new data (this could be done via an automated script that parses the provided data files into SQL updates). Because the data model is stored in the DB, updating it server-side immediately makes the new data available to all users on next page load – no individual client downloads needed.

    * We will document and adhere to proper API versioning and use JSON for data exchange. FastAPI makes it easy to define data models (using Pydantic) to ensure the frontend and backend have a clear contract for the data structures.

  * **Framework considerations:** *Why FastAPI and possibly Django?* FastAPI will give us a high-performance REST API with async support (useful if we have to call external services for updates or handle many concurrent requests). It’s lightweight and will likely cover all our needs for the API layer. **Django** could be introduced mainly for its ORM and admin interface, if we want a quick way to view/edit data or manage users. One approach is to use **Django as the base** (with Django REST Framework for APIs) – this gives a powerful admin console for free – but that might be heavyweight if we don’t need the full stack. Another approach: use FastAPI \+ SQLAlchemy \+ Alembic migrations for a slimmer solution, and possibly integrate something like **Piccolo Admin** or a custom admin for basic data management. Given the requirements, FastAPI with SQLAlchemy is likely sufficient for the MVP, and we can incorporate a Django admin in a later phase if needed (or run Django as a separate service purely for admin).

* **Backend Services – Scalability & DevOps:** We will containerize the application for deployment on **GCP (Google Cloud Platform)**. The target is to have a **Dockerized** solution that can run both locally (for development and for end-users who may want an offline local instance) and on the cloud (to serve many users). The Docker setup could be as follows:

  * A base image for the backend (Python 3.x slim image). The Dockerfile will install our Python dependencies (FastAPI, etc.), copy the application code, and launch Uvicorn server. We might use Gunicorn with Uvicorn workers for production for better scaling. This container, when run, hosts the API.

  * A separate image for the frontend (NodeJS build environment to produce a static bundle). In production, we can actually serve the static React files via a CDN or via the backend. One convenient approach is to have a **single container** serve both: e.g., once we build the React app (the static files), the Python backend (FastAPI) can be configured to serve those static files (using Starlette’s static files support). This way the whole app (API \+ UI) is one deployment unit. Alternatively, use a separate Nginx or Firebase hosting for the frontend. For simplicity in MVP, bundling them is fine.

  * **Database**: PostgreSQL will run as a managed service in production (Cloud SQL on GCP) or as a local Docker container for development. We will set up database migrations (using Alembic or Django migrations) so the schema can be version-controlled.

  * We will include configuration for cloud deployment (for example, a Helm chart or GCP Cloud Run settings) but since the detail is just “on GCP,” we can initially deploy on **Cloud Run** or **App Engine** (both can directly run our Docker container). Cloud Run might be ideal for a containerized web service, and we can use a separate Cloud SQL for the Postgres. We’ll ensure environment variables or secrets are used for DB credentials, etc.

* **Feature Parity and Improvements:** The rewrite will **preserve all features**: the ability to create builds with any archetype, all powers and enhancements up to the Homecoming 2025.7.1111 release, with accurate calculations of powers and bonuses. In fact, by using a central server, we can improve some aspects:

  * **Consistency and Updates:** Instead of each user needing to download updates, the server’s database will be updated by us – so all users instantly use the latest data. This eliminates the complex bootstrapper from the client side. The web client could still display a notification, “Game database updated to version X”, but it doesn’t need to download files – it simply pulls from the server’s API which now serves the new data.

  * **Performance:** A concern in a web app is performance of data-heavy operations. We can mitigate this with careful design:

    * Many operations (like listing powers or enhancements) are just data fetches, which Postgres can handle quickly especially with indexing. We can implement caching at the API layer (using FastAPI caching or an in-memory cache like Redis for frequent queries) to speed up responses.

    * For calculations, if done on server, ensure they are efficient (possibly port over or translate the formulas from C\# to Python, writing unit tests to verify identical results).

    * The client can handle most user interactions without server calls (once it has the initial data, it’s mostly a matter of selecting and showing results). So, a lot of the app will run in the browser – meaning the server primarily serves as data provider and occasional calculator, which scales well.

  * **Scalability:** GCP can scale the backend containers as needed. The stateless nature of the API (just serving data and calculating on request) means we can run multiple instances behind a load balancer if our user base grows. The database can be scaled vertically (and we can add read replicas if necessary for heavy read load).

  * **Local Offline Mode:** We’ll still provide a way for users to run the app offline if desired (similar to how the original can run without internet after installation). Using Docker, an advanced user could run the Postgres and API container on their own machine and open the React app locally – effectively running their personal instance. We might not target this for non-technical end-users in MVP, but our Docker setup will allow it (fulfilling the idea of a “locally runnable version”).

  * **Docker Distribution:** To mimic the ease of the original (which had a simple installer), we can distribute a Docker image or docker-compose setup. For example, provide a pre-built Docker image that contains a lightweight webserver with the React app and data pre-packaged (for a truly offline solution, we’d bake the data into a SQLite database in the container, perhaps). Then “running Mids Reborn locally” would be as simple as `docker run mids-web:latest` and opening a browser to `localhost`. This might be a stretch goal, but it’s achievable given containerization.

Overall, the new architecture will be a **clear separation of concerns**:

* The **React frontend** handles presentation and user interaction.

* The **Python backend (FastAPI)** handles data access and game logic.

* The **Postgres database** stores the authoritative game data (and later, user accounts and saved builds).

* The system will be easier to maintain: updating game data means running a script or admin action once, rather than deploying a patcher to every user. The web stack is modern and aligned with current development best practices, making it more welcoming for open-source contributors as well.

Security considerations will be addressed (ensuring the API is read-only for game data for general users, and any admin update interface is protected; also, if user accounts are added, proper auth & HTTPS in production).

In summary, the rewritten app will transform Mids Reborn into a **cloud-enabled, platform-agnostic** service: users just visit a website (or run a local container) to plan their characters. This modern approach will retain the rich functionality of the original while providing easier updates and potential for new features (like build sharing, community integration, etc.).

## **Development Roadmap (Epics, Tasks, and Sub-Tasks)**

Below is a detailed development plan for implementing the new web-based Mids Reborn. The plan is organized into **Epics** (major goals or milestones), each broken down into specific **Tasks**, which are further subdivided into **Sub-tasks** as needed. This roadmap covers the project from initialization to a minimum viable product (MVP) that can load the Homecoming 2025.7.1111 database and support character build planning, and beyond towards deployment.

### **Epic 1: Project Setup and Planning**

**Goal:** Establish the project structure, repositories, and development environment for the frontend and backend.

1. **Set Up Repositories and Codebase Structure**

   * *Sub-task 1.1.1:* Initialize a new Git repository (or mono-repo) for the project. Create folders for `frontend/` and `backend/` components.

   * *Sub-task 1.1.2:* Choose a naming convention and baseline license/readme. Document the project goal and stack in the README (mentioning React, FastAPI, Postgres, etc.).

   * *Sub-task 1.1.3:* Configure version control and CI pipeline (set up GitHub Actions or similar to lint/test/build on pushes).

2. **Frontend Scaffold (React)**

   * *Sub-task 1.2.1:* Bootstrap a React app (using Create React App or Vite for a lightweight setup). Set the project to use TypeScript (recommended for easier maintenance and catching errors early) or JavaScript as per team preference.

   * *Sub-task 1.2.2:* Install base dependencies (e.g. React Router for navigation if needed, a UI component library like Material-UI, state management like Redux or Context API if complexity grows).

   * *Sub-task 1.2.3:* Set up a basic file structure for React (components, services for API calls, styles). Verify that the dev server runs and you can open a default page.

3. **Backend Scaffold (FastAPI \+ ORM)**

   * *Sub-task 1.3.1:* Create a Python virtual environment and initiate a FastAPI project. Install FastAPI and Uvicorn, plus an ORM library (SQLAlchemy with Alembic for migrations, or Tortoise ORM, etc.).

   * *Sub-task 1.3.2:* Set up the basic FastAPI application file (e.g. `main.py`) with a simple health-check endpoint (e.g. `GET /ping` returning “pong”) to verify the server runs.

   * *Sub-task 1.3.3:* Configure CORS in FastAPI to allow the React dev server to call the APIs (during development).

   * *Sub-task 1.3.4:* Decide on ORM vs Django: If using Django, run `django-admin startproject` and integrate Django REST framework; otherwise, configure SQLAlchemy models manually. (This task includes making that architectural decision early.)

   * *Sub-task 1.3.5:* Set up database connection config (for now, can use SQLite or a local Postgres instance for dev). Verify the backend can connect to DB.

4. **Docker Environment**

   * *Sub-task 1.4.1:* Write a `Dockerfile` for the backend service (base image python:3.11-slim, copy code, pip install, expose port, command to run Uvicorn).

   * *Sub-task 1.4.2:* Write a `Dockerfile` for the frontend (could use node:16-alpine to build, then nginx:alpine to serve static files, or simply use multi-stage and serve via a lightweight server). Alternatively, plan to serve frontend via the backend (in which case, just ensure frontend build outputs can be integrated).

   * *Sub-task 1.4.3:* Create a `docker-compose.yml` for local development that brings up: the Postgres database, the backend (mount code for hot-reload in dev), and the frontend (if needed). Ensure `docker-compose up` can start the whole stack in development mode.

   * *Sub-task 1.4.4:* Test the Docker setup: verify the backend container can talk to the Postgres container (adjust environment variables accordingly), and that the frontend container can reach the backend’s API (network configuration).

### **Epic 2: Data Model & Database Integration**

**Goal:** Define the database schema and import the City of Heroes data (Homecoming 2025.7.1111) into the new system.

1. **Design Database Schema**

   * *Sub-task 2.1.1:* Identify all data entities from the original app: Archetype, Powerset, Power, Enhancement, SetBonus, Salvage, Recipe, etc., and their relationships. Design an ER diagram or outline. (E.g., **Archetype** has many **Powersets**; **Powerset** has many **Powers**; **Power** may have multiple effects or enhancements; **Enhancements** can belong to **Sets** which have set bonuses, etc.)

   * *Sub-task 2.1.2:* Translate the design into SQLAlchemy models or Django models. Define fields with appropriate types (e.g., integers for IDs, floats for percentages, text for descriptions). Include foreign keys for relationships and indexes on important fields (like names or IDs for fast lookup).

   * *Sub-task 2.1.3:* Run migrations (or create the database via sync) to apply the schema to the Postgres database. This yields empty tables ready to be filled.

2. **Data Import Utilities**

   * *Sub-task 2.2.1:* Write scripts to convert existing data into the new database. We have a few possible data sources:

     * Use the Mids Reborn data files directly: for Homecoming, we can parse the `.mhd` files. This might require writing a small parser that mimics what the C\# `DatabaseAPI` does (reading binary data with specific structure). The easier route: the Mids manifest might offer the database in a more accessible format (e.g., an archive of CSV or JSON). Investigate if the update manifests or the Homecoming community provide a raw data dump (perhaps an official JSON of powers). If not, we’ll proceed with parsing.

   * *Sub-task 2.2.2:* Implement a parser for binary .mhd files (if needed). For example, for `I12.mhd`, replicate the reading logic: read header, then sequentially read archetype count, archetypes, powersets, etc. The format is likely length-prefixed strings and arrays of structures (the original C\# uses BinaryReader to deserialize). Because this is complex, consider if the original Mids Reborn could be extended to output JSON – maybe we can run the original in a mode to export data. If not, proceed with a custom parser or use the in-memory data via automation:

     * One creative approach: Write a small C\# program (or modify Mids Reborn code) to load the data and then serialize it to JSON using the existing classes. Since we have the source, we could create a console app that references MidsReborn.Core, calls `LoadData` on Homecoming, then dumps the data classes to JSON. This one-time effort might be quicker than writing a full parser in Python.

   * *Sub-task 2.2.3:* Once data is available in an intermediary form (JSON or CSV), write a Python script to insert it into the Postgres database via the ORM. Ensure to maintain referential integrity (e.g., when inserting powersets, link them to the correct archetype ID from the Archetypes table, etc.). Use SQLAlchemy session or Django ORM calls in bulk for efficiency.

   * *Sub-task 2.2.4:* Verify the imported data: pick a few examples (e.g., an Archetype “Blaster”, ensure its powersets count matches expectations, check a known power’s values). This is to ensure no data loss or corruption in the import.

3. **Validation against Original**

   * *Sub-task 2.3.1:* Cross-check counts: The number of archetypes, total powers, total enhancements, etc., in the new DB should match those from the original data (for Homecoming). We can get these numbers either from the original app’s data (maybe in the Mids logs or by querying the loaded objects count). If they match, it increases confidence in the import.

   * *Sub-task 2.3.2:* If possible, run a small scenario: for example, pick a specific build that was known to the original (some combination of powers) and ensure all those elements exist in the new DB. This is essentially a sanity test for completeness.

4. **Automating Future Imports**

   * *Sub-task 2.4.1:* (Optional, but good to plan) Write a general script or document a procedure for updating the database when a new game version is released. For MVP, document how to run the import for Homecoming data again. In the future, we might incorporate this into the app (like an admin endpoint to trigger data update, which could fetch new data from a URL, then run the import automatically). Documenting it now sets the stage for implementing it later in the roadmap.

### **Epic 3: Backend API Development**

**Goal:** Implement the backend functionality to serve data and perform calculations, aligning with all features needed by the frontend.

1. **Core Data Endpoints (Read Operations)**

   * *Sub-task 3.1.1:* Implement `GET /api/archetypes`: returns list of all archetypes with key details (id, name, origin list, maybe primary/secondary set names). This is the first call the frontend will likely make to populate the archetype selector. Ensure to include all data needed for an archetype (maybe description, hit point modifiers, etc., for a future detail view).

   * *Sub-task 3.1.2:* Implement `GET /api/archetypes/{id}`: returns detailed info for a specific archetype, including its powersets. Alternatively, create a separate endpoint for powersets. We might do `GET /api/archetypes/{id}/powersets` to list all primary and secondary powersets for that archetype. Each powerset object should include its powers summary or at least an ID to query powers separately.

   * *Sub-task 3.1.3:* Implement `GET /api/powersets/{id}`: returns details of a powerset, including the list of powers in it (with each power’s name, level availability, etc.). If not done in previous step, we can fetch powerset by ID (the frontend will have powerset IDs from the archetype query).

   * *Sub-task 3.1.4:* Implement `GET /api/powers/{id}`: returns detailed info for a single power. This might include descriptions, base damage, endurance cost, recharge, effects, etc. The frontend might call this when showing a tooltip or a detailed view of a selected power. Alternatively, we may embed enough power info in the powerset response to avoid too many calls. We should find a balance (maybe include full power info in powerset listing to minimize API round-trips).

   * *Sub-task 3.1.5:* Implement `GET /api/enhancements` and related endpoints: The enhancement system is complex – likely we need:

     * `GET /api/enhancement-sets`: list of all IO sets (with their names, set bonuses).

     * `GET /api/enhancement-sets/{id}`: details of one set including the enhancements in it.

     * `GET /api/enhancements?powerId=X`: query which enhancements are valid for a given power (e.g., based on origin/type of the power). This logic replicates what original does when showing which enhancement slots accept which enhancements. We can derive from each power’s allowed enhancement categories (which should be in data). Perhaps store a mapping of power \-\> allowed enhancement types. This query helps front-end populate only the relevant enhancements when user opens an enhancement slot on a power.

     * Also, an endpoint for **set bonuses** might be needed: e.g., given a list of slotted enhancements, return the cumulative set bonus effects. However, that could also be computed on frontend if data is available.

   * *Sub-task 3.1.6:* Implement any miscellaneous data endpoints: e.g., `GET /api/incarnates` if incarnate abilities are stored and needed, or `GET /api/salvage` and `GET /api/recipes` if we plan to show crafting info. For MVP, focus on core build planning, which might not need salvage/recipe details immediately (original has an invention planner, but we can postpone that).

2. Each of these endpoints should use the ORM to retrieve data and serialize to JSON. Using Pydantic models in FastAPI will make serialization easy (define a Pydantic schema for Archetype, for Power, etc.). Ensure to exclude internal IDs or confusing fields; keep it user-relevant.

3. **Build Simulation & Calculation Endpoints**

   * *Sub-task 3.2.1:* Identify the key calculations the original app performs: examples include totals for defense/resist if multiple powers are toggled, attack damage with enhancements, endurance consumption, etc., as well as validation like “is this build concept valid (no too many powers from pools, etc.)”. For MVP, we can simplify – we may not simulate combat, but we do want things like checking enhancement slot limits and possibly computing set bonuses.

   * *Sub-task 3.2.2:* Implement `POST /api/calculate` (or `/api/build/evaluate`): The frontend can POST the current build (in some structured format, e.g. JSON listing chosen archetype, powers, and slotted enhancement IDs). The backend then responds with computed aggregate stats. Initially, we can implement minimal calculation: e.g., take all slotted enhancements, sum their enhancement percentages for each category (damage, accuracy, etc.) and return that, combine with base power values to get modified values. Include also any set bonus contributions.

   * *Sub-task 3.2.3:* Write unit tests for the calculation logic. We can create a few scenarios with known outcomes (perhaps using examples from the original app’s forums or manual calculations) to ensure our results align. For instance, if a power has base 100 damage and two enhancements of \+25% damage, final should be 150 (simple example). More complex: check that enhancement rules (like ED caps – Enhancement Diversification limits – if those exist on Homecoming) are applied. This might be advanced, so note such rules for future.

   * *Sub-task 3.2.4:* If any calculations are too complex to implement by hand, consider porting logic: The original code for calculations might be found in classes under `Core.Base.Data_Classes` or `Core.Statistics`. We could translate that logic to Python. This ensures consistency with the original. Mark any complex formula to revisit for accuracy (could be a later epic to refine the “power math” once basic functionality is in place).

4. **Write/Modify Operations (if needed for MVP)**

   * The primary use-case (build planning) doesn’t require the server to permanently store user data unless we introduce accounts. For MVP, we might not implement user login; builds can be ephemeral or downloaded by the user. So, we may not need server-side persistence for user builds initially.

   * However, consider implementing a **save format**:

     * *Sub-task 3.3.1:* Define a JSON schema for a build (list of chosen powers and enhancements). This can be used to allow users to save their build locally (e.g., by downloading a JSON file) and later load it.

     * *Sub-task 3.3.2:* Implement `POST /api/build/encode` that takes a build JSON and returns a compact string or file (could be simply a base64 or a zip of the JSON) – analogous to how the original might export to a file or generate a forum code. Similarly, a `POST /api/build/decode` to accept an uploaded file or code and return the build JSON for the frontend to load. These endpoints help users share builds easily. They can be added once basic planning works.

   * If user accounts are planned:

     * *Sub-task 3.3.3:* (Future consideration) Implement authentication (e.g. JWT or session) and endpoints `GET /api/user/builds` and `POST /api/user/builds` to save builds to the database tied to a user. This would require a User model and login system (could use OAuth or basic email login). This is beyond MVP, but worth planning as an epic on its own later.

5. **Testing the API**

   * *Sub-task 3.4.1:* Create automated tests for each endpoint (using PyTest or FastAPI’s test client). Test that each GET returns expected structure and data for known inputs. For example, call `/api/archetypes` and ensure “Blaster” is in the results, etc.

   * *Sub-task 3.4.2:* Test edge cases: invalid IDs (ensure a 404 or appropriate error for e.g. `/api/powers/99999` if not found), empty inputs, etc.

   * *Sub-task 3.4.3:* If calculation endpoint exists, test it with a known simple build and verify the output.

   * *Sub-task 3.4.4:* If using test database, include some sample data or use the actual imported data for tests. Continuous integration should run these tests to catch regressions.

### **Epic 4: Frontend Application Implementation**

**Goal:** Build the React UI to allow users to perform all the tasks the WinForms app could: select an archetype, choose powers, slot enhancements, and view results.

1. **UI Layout and Navigation**

   * *Sub-task 4.1.1:* Design a layout structure: likely a single-page interface (since in the original everything is mostly on one window). We can have sections or panels for different parts of the build:

     * A top or side panel for general character info (Archetype, Origin, maybe Incarnate selection).

     * A main panel for power selection (perhaps tabs or accordions for Primary, Secondary, Pool powers, Epic/Ancillary powers).

     * A section for enhancement slots and slotting.

     * A sidebar or bottom area for calculated totals / stats summary.

   * *Sub-task 4.1.2:* Implement a basic layout with placeholder components for each area. Use a responsive grid or flexbox so that it can be resized (target standard desktop first, but consider future mobile friendliness).

   * *Sub-task 4.1.3:* Set up React Router if we plan to support multiple routes (not strictly necessary for an SPA that’s mostly one screen, but if we later add things like a list of saved builds or an about page, routing might help). For MVP, can skip routing complexity and keep everything in one view with conditional renders.

   * *Sub-task 4.1.4:* Integrate a UI theme and test some styling (light vs dark mode perhaps, since original has a dark theme). Ensure the base font and colors are legible.

2. **Archetype and Powerset Selection**

   * *Sub-task 4.2.1:* Create a **ArchetypeSelector** component. On load, fetch archetypes from `/api/archetypes` and store them in state. Populate a dropdown or list with these. When the user selects an archetype:

     * Save the selection in a global state (e.g., a `currentBuild` context or in a parent component state).

     * Trigger fetch of that archetype’s powersets (either use the detailed data if we got it in one call, or call `/api/archetypes/{id}/powersets`).

   * *Sub-task 4.2.2:* Create **PowersetSelection** components for Primary, Secondary, and Pool powers:

     * These will display the list of available powersets in each category for the chosen archetype. For example, once archetype is picked, populate Primary powerset list with all primary sets for that AT. Do similarly for Secondary. Pool powers may be global (not tied to AT, except maybe origin pool restrictions, but Homecoming allows 4 pools out of many).

     * Allow the user to choose one primary and one secondary (for pools, possibly up to 4 pool picks out of the available). This likely involves checkboxes or multi-select for pool powersets.

     * When a powerset is selected, fetch its powers (if not already loaded) and display them (likely in the next step).

   * *Sub-task 4.2.3:* Display Powers within each selected powerset:

     * For Primary and Secondary: list all powers (each power has a level availability – e.g. level 1,2,..., so show them in order). The user should be able to “pick” which powers their character has. In City of Heroes, a character can skip some powers, but must take at least 1 power every level from 1 to 49, with certain number from primary/secondary, etc. Mids usually lets you toggle powers on/off up to the limit of how many picks you have by level.

     * Implement a mechanism to choose powers: possibly checkboxes next to each power name, or draggable to a “build” timeline. For MVP, a simpler approach: assume the user will eventually pick 24 powers (level 1-50 grants \~24 picks including incarnates). We can just allow any selection but keep a count and enforce max picks.

     * If possible, implement level tracking: e.g., an array of 50 levels, user assigns powers to specific levels. This is more advanced (Mids does that to ensure legality). For MVP, we might skip strict level assignment and just ensure number of powers doesn’t exceed the allowed count. We can refine this in a later iteration.

     * Use state to track selected powers. When a power is selected or deselected, update the build state.

     * If a power has prerequisites (some powers require another first), the data should tell us. Enforce that by disabling powers until prereq is chosen (the original app likely greys them out).

   * *Sub-task 4.2.4:* Incarnate powers (if included): The Homecoming DB includes incarnate abilities (Alpha, Judgement, etc.). Provide UI to select one ability for each incarnate slot. This might be a simple dropdown per incarnate slot, since incarnates are separate from normal power picks. We should include this for feature parity (though Homecoming has incarnate levels outside the 1-50 leveling scheme).

   * *Sub-task 4.2.5:* As the user selects archetype and powersets, update any relevant UI fields (like an Archetype description panel, or a count of how many powers picked vs available).

3. **Enhancement Slotting Interface**

   * *Sub-task 4.3.1:* For each power the user has chosen in their build, display its enhancement slots. Initially, at level 1 a power has 1 slot, and you gain slots as you level up which you can assign to powers (the original app lets you allocate slots to different powers). Implement a way for user to add slots to powers (e.g. a “+” button to add a slot to a particular power until the total slots equals the allowed number – slots are equal to level \- 1 beyond first, total 24 enhancement slots to allocate by 50, plus inherent Stamina/Health slots per server rules).

     * This is a complex aspect: Mids Reborn handles slot allocation. For MVP, we might simplify by pre-allocating a reasonable number of slots per power or assume default allocation. But since slotting is core to build optimization, better to allow user control.

     * Perhaps start with a simplified model: each power gets a fixed number of slots equal to its maximum (e.g., 6 slots, which is CoH max). The user can then slot enhancements without worrying about allocation. This deviates from game rules (game limits total number of slots distributed), but in an MVP it’s a user-friendly simplification. We will note to implement actual slot leveling in future.

   * *Sub-task 4.3.2:* When a user clicks on an empty slot, open an **EnhancementPicker** dialog/popover:

     * This component fetches the list of **enhancement types** that can go in that power. For example, a damage power can accept damage enhancements, accuracy, recharge, etc. The server can provide this info (via `/api/enhancements?powerId=X` or by listing allowed enhancement categories in the power data).

     * Show the enhancements grouped by category or by sets. E.g., show all Single-Origin (SO) enhancements for that category, IOs, set IOs, etc. Because the list can be long, provide filters or tabs (Attuned IO sets vs standard IO vs SO).

     * The user selects an enhancement to slot. The slot UI then shows an icon or name of that enhancement.

     * Ensure that the user can slot at most one of each unique enhancement unless it’s attuned vs regular difference (the game rules allow only one of each enhancement effect type in a power except in very limited cases). Mids enforces “slotting rules” (like no two of the same IO set piece in one power). We will implement checks: if user tries to put a duplicate, either prevent or warn.

   * *Sub-task 4.3.3:* Set Bonus Display: If the user has multiple enhancements from the same set across their powers, show the set bonuses active. We can have a small panel listing active set bonuses. The logic: whenever the build state updates, calculate how many pieces of each set are slotted and determine which bonuses apply (set bonuses usually unlock at 2,3,4,5,6 pieces).

   * *Sub-task 4.3.4:* Power Enhancement effects: We should reflect how enhancements alter a power. E.g., if 3 damage enhancements are slotted, the power’s damage should show increased. The calculation engine (either in frontend or backend) will provide modified values. E.g., after each change, we can call the `calculate` API with the build, or do a local calculation with the same logic. For MVP, a simple approach: just list the enhancements and rely on the overall stats panel for feedback. For more dynamic UI, we might show on each power how much its damage or recharge is improved. This can be done if we either compute on the fly or have the backend return per-power stats.

4. **Stats Summary and Feedback**

   * *Sub-task 4.4.1:* Create a **SummaryPanel** that shows overall character stats of interest: e.g., offense (damage bonus, to-hit bonus), defense/resistance totals by type, health and endurance totals, recharge bonus, etc. Many of these derive from powers (toggles that give defense) and set bonuses.

   * *Sub-task 4.4.2:* Whenever the build changes (power or enhancement added/removed), update this summary. If using the backend calculate endpoint, send the build and update summary from the response. If calculating in front-end, run the calculations (could reuse some of the backend logic if we port it in JS or call a WebAssembly version of it). Initially, it’s acceptable to show a simpler summary (like just list chosen powers and slotted enhancements) if detailed math is not ready. But target to have at least totals for each defensive category and damage bonus, since players use those to gauge build effectiveness.

   * *Sub-task 4.4.3:* Include validation warnings in the summary: e.g., if the build overspent slots or picked too many powers for their level, highlight that. Or if an invalid combination is chosen (like two travel powers when maybe only one is allowed pre-50, etc.), notify the user. This helps users correct their build. The original Mids indicates such issues with red text or warnings; we can do tooltips or warning messages.

5. **Polish UI & User Experience**

   * *Sub-task 4.5.1:* Add tooltips and info popups. Each power should have a tooltip with its description and numbers (damage, recharge, etc., including current values with enhancements). Each enhancement could have a tooltip explaining what it does. Use a library for rich tooltips or build custom ones.

   * *Sub-task 4.5.2:* Implement a way to reset or clear selections (a “New Build” button).

   * *Sub-task 4.5.3:* Implement import/export of builds on the UI side. E.g., a “Save Build” button that either downloads a file (JSON or some .mids format) or copies a code to clipboard, and a “Load Build” to import. This ties into the earlier backend tasks if using the API, or can be done entirely front-end by packaging the current state.

   * *Sub-task 4.5.4:* Ensure mobile/responsive design considerations. While a desktop-like interface is complex on mobile, we can at least ensure the layout doesn’t break on smaller screens. Possibly use collapsible sections for different parts or allow horizontal scrolling for large tables.

6. **Frontend Testing**

   * *Sub-task 4.6.1:* Write unit tests for React components (if using testing libraries like Jest/React Testing Library). Test critical components: that selecting an archetype triggers the loading of powersets, that the enhancement selection logic enforces rules, etc.

   * *Sub-task 4.6.2:* Perform manual end-to-end testing: run the backend and frontend together and simulate creating a full build for a couple of archetypes. Verify that the data shown matches known values from the original app (for example, pick a simple power and check that its base damage matches the known value from in-game or original Mids).

   * *Sub-task 4.6.3:* Usability testing: get feedback on the UI layout from a few users (could be colleagues or community testers) to ensure the interface is intuitive. Adjust things like labeling, button placement, instructions as needed.

### **Epic 5: Deployment and DevOps**

**Goal:** Deploy the MVP application to a cloud environment (GCP) and ensure it can be easily run locally via Docker.

1. **Prepare for Production Build**

   * *Sub-task 5.1.1:* Update backend configuration for production: use environment variables for database URL, secret keys, etc. Ensure debug modes are off. Possibly integrate Gunicorn to serve FastAPI with multiple workers for efficiency.

   * *Sub-task 5.1.2:* Build the frontend for production (`npm run build` or equivalent), and configure the backend to serve the static files. Verify that the React app works correctly when served from the backend (check paths, etc.).

   * *Sub-task 5.1.3:* Configure CORS or allowed origins accordingly (if serving from same domain in prod, might disable the wide-open CORS used in dev).

2. **Docker Image Finalization**

   * *Sub-task 5.2.1:* Ensure the Dockerfile for backend is multi-stage if needed (to reduce image size). Possibly incorporate the frontend build into the backend image (copy build output into a `static/` directory served by FastAPI). This yields a single container that serves both API and UI.

   * *Sub-task 5.2.2:* Perform a test: run the container locally, pointing it to a local Postgres with the imported data. Access the app via `localhost` and confirm all works in a production-similar setting.

   * *Sub-task 5.2.3:* Publish the Docker image (to a registry or container repository) for deployment. Tag it as `mids-web:0.1.0` (or using semantic versioning).

3. **Cloud Deployment (GCP)**

   * *Sub-task 5.3.1:* Set up a Postgres instance on GCP (Cloud SQL) and load the data. Alternatively, if the data is not too large, use a Cloud SQL import feature or run the import script on the cloud. Ensure connectivity details (we might need a VPC connector if using Cloud Run to connect to Cloud SQL, or use Cloud Run’s built-in Cloud SQL proxy).

   * *Sub-task 5.3.2:* Deploy to **Cloud Run** (serverless containers) or another service:

     * If Cloud Run: create a service, set the image, configure environment variables (DATABASE\_URL, etc.), set concurrency and auto-scaling limits. Allow unauthenticated access (for a public app).

     * If GKE (Kubernetes): set up a cluster and use a Deployment \+ Service with LoadBalancer or Ingress. This is heavier, so Cloud Run is likely simpler initially.

     * Alternatively, use **App Engine Flex** with the Docker image.

   * *Sub-task 5.3.3:* Configure a domain or use the provided Cloud Run URL. If custom domain (e.g. midsreborn.app or similar), set up DNS. Ensure SSL (Cloud Run provides HTTPS by default on its domain, and on custom domain via managed cert).

   * *Sub-task 5.3.4:* Test the deployed version thoroughly. Check that all API endpoints are reachable and fast (GCP region selection near user base if relevant). Check that static files are served correctly. Try a full user flow in the production environment.

4. **Docker Distribution for Local Use**

   * *Sub-task 5.4.1:* Create documentation for how users can run the app locally via Docker. Possibly provide a `docker-compose.yml` that brings up the app with an embedded database:

     * We could use SQLite for a self-contained local run (bake the SQLite with data into the image). Or have the compose also run a Postgres container and load data on startup (this could be slow, so SQLite might be better for a one-off).

     * Ensure that the local run does not attempt to fetch updates (or if it does, it's optional). We want it to work offline just like the old app. This might mean packaging the latest data with the container and not updating until the user chooses to pull a new image.

   * *Sub-task 5.4.2:* Test the offline container: simulate no internet and run the container, confirm the app still works with the packaged data.

   * *Sub-task 5.4.3:* Publish this image or provide instructions so that less technical users can use it. (E.g., “Install Docker, then run `docker run -p 8000:80 midsreborn/web:latest` and open [http://localhost:8000”](http://localhost:8000%E2%80%9D/)).

5. **Monitoring and Logging**

   * *Sub-task 5.5.1:* Set up application logging in backend for production (similar to how Serilog was used – in FastAPI we can use Python’s logging module to log important events like errors or update checks). Ensure these logs can be viewed on GCP (Cloud Run logs, etc.).

   * *Sub-task 5.5.2:* Set up error tracking (maybe integrate Sentry or a simple email alert) for runtime exceptions, so we know if users encounter issues.

   * *Sub-task 5.5.3:* Monitor performance: enable GCP Cloud Monitoring or custom metrics for request latency, etc. Ensure the app remains responsive under load; adjust instance size or count if needed.

### **Epic 6: Optimization and Feature Enhancements (Post-MVP)**

*(This epic goes beyond the initial MVP but outlines improvements and refactoring that align with “areas that can be optimized, re-architected, deleted, changed” as mentioned.)*

1. **Performance Optimizations**

   * Profile the application (both front-end rendering and back-end query performance). Identify any slow API calls (maybe loading all enhancements is heavy – we might implement pagination or better indexing).

   * Implement caching on the API for static data endpoints (e.g., archetypes list changes only when data updates, so it can be cached in memory or behind a CDN).

   * Utilize browser localStorage or IndexedDB to cache game data on the client after first load, to reduce subsequent loads (e.g., cache the powers data so that if the user reloads the page, we don’t re-fetch everything every time – at least until a new version is detected).

2. **Better Build Validation**

   * Introduce the full ruleset for build validity: enforce level-based power picks, pool selection limits, etc., on the client with guiding UI and on the server for double-check. Possibly provide a “level-up simulator” UI where users pick which level they take each power and slot.

   * Add warnings or info for missing travel power, etc., similar to how original might warn about unpicked powers.

3. **User Accounts and Cloud Saving**

   * Implement a login system (could integrate with Gmail/Discord for the community) so that users can create an account and save builds to the cloud. This would allow them to access their builds from any device and share via a link.

   * Provide privacy settings for builds (public link or private).

   * Possibly integrate with the Discord server (for example, a bot could retrieve builds from the web app if given a code).

4. **In-Game Integration (Long-term)**

   * Explore integration with City of Heroes servers: e.g., fetch a character’s data via an API (if Homecoming provides one) to pre-load an existing character into the planner, or export a build in a format that game servers or other tools accept.

   * This is an advanced feature that goes beyond the current desktop app, but a web architecture might allow it.

5. **Continual Data Updates**

   * Automate the data update pipeline. For example, if Homecoming releases a new update, have a GitHub Action or a scheduled job that fetches the new manifest, downloads data, runs the import, and updates the cloud database. This reduces manual work and ensures users always have the latest info.

   * Also, allow the app to support multiple “live” databases concurrently (if we want to support Homecoming and Rebirth simultaneously on the site). We could allow the user to choose the server data set in the UI (similar to the desktop version’s ability). This would entail our API serving data from multiple schemas or a combined schema with a “realm” field. It’s doable – perhaps an epic of its own – but planning for it ensures we don’t hard-code assumptions for Homecoming only.

6. **Clean-up and Deprecation**

   * As the web app matures, deprecate components that were temporary:

     * If any simplifications were made (like not implementing slot allocation by level), re-architect those parts to be closer to game mechanics now that core is done.

     * Remove any legacy or test code. Refactor duplication (maybe some logic is in both frontend and backend for calc – decide a single source or use a shared library or WebAssembly module for calculation so logic is not duplicated in two languages).

     * Optimize data storage if needed (if certain tables are rarely used or can be merged, adjust schema with migrations).

Finally, thorough **documentation** and **community feedback** will be ongoing tasks. We will maintain docs for developers (how to contribute, how data schema works) and for users (how to use new web UI, differences from desktop, etc.). Each sprint or iteration will involve user testing, especially since this app serves a dedicated community who can provide valuable input to refine the tool.

By following this roadmap, we’ll achieve a modern web-based Mids Reborn that successfully replicates the original’s capabilities and sets the stage for easier updates and future enhancements. The MVP will prove out the concept by loading the Homecoming database and allowing basic build creation on the web, and subsequent epics will fill in any remaining gaps and polish the experience.

