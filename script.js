const API_URL = "http://127.0.0.1:5000";

function openLoginModal() {
    let modal = document.getElementById("authModal");

    if (!modal) {
        modal = document.createElement("div");
        modal.id = "authModal";
        modal.className = "modal";

        modal.innerHTML = `
            <div class="modal-box">
                <button class="close" onclick="closeAuthModal()">×</button>

                <div class="tag">WELCOME BACK</div>

                <h2>Login to TripCircle</h2>

                <p class="modal-text">
                    Sign in to continue planning your trips.
                </p>

                <form id="loginForm">

                    <div class="form-group">
                        <label>Email</label>
                        <input
                            type="email"
                            id="loginEmail"
                            placeholder="Enter your email"
                            required>
                    </div>

                    <div class="form-group">
                        <label>Password</label>
                        <input
                            type="password"
                            id="loginPassword"
                            placeholder="Enter your password"
                            required>
                    </div>

                    <button
                        type="submit"
                        class="btn btn-primary modal-submit">
                        Login →
                    </button>

                </form>

                <p style="
                    text-align:center;
                    margin-top:16px;
                    font-size:12px;
                    color:#7c838d;
                ">
                    Don't have an account?
                    <button
                        type="button"
                        onclick="showRegisterModal()"
                        style="
                            border:none;
                            background:none;
                            color:#e96d3d;
                            font-weight:700;
                            cursor:pointer;
                        ">
                        Register
                    </button>
                </p>
            </div>
        `;

        document.body.appendChild(modal);

        document
            .getElementById("loginForm")
            .addEventListener("submit", loginUser);
    }

    modal.classList.add("active");
}


async function loginUser(event) {

    event.preventDefault();

    const email =
        document.getElementById("loginEmail").value.trim();

    const password =
        document.getElementById("loginPassword").value;

    try {

        const response = await fetch(
            `${API_URL}/api/login`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            }
        );

        const result = await response.json();

        if (!response.ok) {
            showToast(result.message);
            return;
        }

        localStorage.setItem(
            "tripCircleUser",
            JSON.stringify(result.user)
        );

        closeAuthModal();

        showToast(
            "Welcome, " + result.user.name + "! 🎉"
        );

    } catch (error) {

        console.error(error);

        showToast(
            "Cannot connect to TripCircle backend."
        );
    }
}


function showRegisterModal() {

    const modal =
        document.getElementById("authModal");

    modal.innerHTML = `
        <div class="modal-box">

            <button class="close"
                onclick="closeAuthModal()">×</button>

            <div class="tag">JOIN TRIPCIRCLE</div>

            <h2>Create your account</h2>

            <p class="modal-text">
                Create an account and start planning your trips.
            </p>

            <form id="registerForm">

                <div class="form-group">
                    <label>Name</label>
                    <input
                        type="text"
                        id="registerName"
                        placeholder="Enter your name"
                        required>
                </div>

                <div class="form-group">
                    <label>Email</label>
                    <input
                        type="email"
                        id="registerEmail"
                        placeholder="Enter your email"
                        required>
                </div>

                <div class="form-group">
                    <label>Password</label>
                    <input
                        type="password"
                        id="registerPassword"
                        placeholder="Enter your password"
                        required>
                </div>

                <button
                    type="submit"
                    class="btn btn-primary modal-submit">
                    Create Account →
                </button>

            </form>

            <p style="
                text-align:center;
                margin-top:16px;
                font-size:12px;
                color:#7c838d;
            ">
                Already have an account?

                <button
                    type="button"
                    onclick="openLoginModal()"
                    style="
                        border:none;
                        background:none;
                        color:#e96d3d;
                        font-weight:700;
                        cursor:pointer;
                    ">
                    Login
                </button>
            </p>

        </div>
    `;

    document
        .getElementById("registerForm")
        .addEventListener(
            "submit",
            registerUser
        );
}


async function registerUser(event) {

    event.preventDefault();

    const name =
        document.getElementById("registerName")
            .value.trim();

    const email =
        document.getElementById("registerEmail")
            .value.trim();

    const password =
        document.getElementById("registerPassword")
            .value;

    try {

        const response = await fetch(
            `${API_URL}/api/register`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    name: name,
                    email: email,
                    password: password
                })
            }
        );

        const result =
            await response.json();

        if (!response.ok) {
            showToast(result.message);
            return;
        }

        showToast(
            "Registration successful! Please login."
        );

        openLoginModal();

    } catch (error) {

        console.error(error);

        showToast(
            "Cannot connect to TripCircle backend."
        );
    }
}


function closeAuthModal() {

    const modal =
        document.getElementById("authModal");

    if (modal) {
        modal.remove();
    }
}
// ==========================================
// SAVE TRIP TO MYSQL
// ==========================================

const originalSaveTrip = window.saveTrip;

window.saveTrip = async function (trip) {

    // Keep the existing localStorage functionality
    if (typeof originalSaveTrip === "function") {
        originalSaveTrip(trip);
    }

    // Get logged-in user
    const user = JSON.parse(
        localStorage.getItem("tripCircleUser") || "null"
    );

    if (!user || !user.id) {
        showToast("Please login before creating a trip.");
        return;
    }

    try {

        const response = await fetch(
            "http://127.0.0.1:5000/api/trips",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    user_id: user.id,
                    name: trip.name,
                    start_location: trip.startLocation,
                    destination: trip.destination,
                    start_date: trip.startDate,
                    end_date: trip.endDate,
                    members: trip.members,
                    progress: trip.progress,
                    itinerary: trip.itinerary,
                    checks: trip.checks
                })
            }
        );

        const data = await response.json();

        if (response.ok) {

            showToast(
                "Trip saved to database successfully! ✅"
            );

            console.log("Database trip:", data);

        } else {

            showToast(
                data.message || "Could not save trip to database."
            );

            console.error("Trip API error:", data);

        }

    } catch (error) {

        console.error("Backend connection error:", error);

        showToast(
            "Backend connection failed."
        );

    }

};
// ==========================================
// LOAD TRIPS FROM MYSQL
// ==========================================

async function loadTripsFromDatabase() {

    const user = JSON.parse(
        localStorage.getItem("tripCircleUser") || "null"
    );

    if (!user || !user.id) {
        return;
    }

    try {

        const response = await fetch(
            `http://127.0.0.1:5000/api/trips/${user.id}`
        );

        const data = await response.json();

        if (!response.ok) {
            console.error("Could not load trips:", data);
            return;
        }

        const databaseTrips = data.trips.map(function (trip) {

            return {
                id: String(trip.id),

                name: trip.name,

                startLocation: trip.start_location,

                destination: trip.destination,

                startDate: trip.start_date,

                endDate: trip.end_date,

                members: Number(trip.members),

                progress: Number(trip.progress),

                itinerary: trip.itinerary || [],

                checks: trip.checks || {},

                packingItems: []
            };

        });

        // Replace browser trips with database trips
        localStorage.setItem(
            "tripCircleTrips",
            JSON.stringify(databaseTrips)
        );

        // Select the newest trip
        if (databaseTrips.length > 0) {

            localStorage.setItem(
                "tripCircleActiveTrip",
                databaseTrips[0].id
            );

            if (typeof renderEverything === "function") {
                renderEverything(databaseTrips[0]);
            }
        }

        if (typeof renderTripList === "function") {
            renderTripList();
        }

        console.log(
            "Trips loaded from MySQL:",
            databaseTrips
        );

    } catch (error) {

        console.error(
            "Failed to load trips from backend:",
            error
        );

    }
}


// Load database trips after page loads
window.addEventListener(
    "load",
    function () {
        loadTripsFromDatabase();
    }
);