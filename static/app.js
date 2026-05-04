const state = {
  building: "house",
  floorId: "house-1",
  bookings: new Map(),
  selectedBed: null,
};

const floorTabs = document.querySelector("#floorTabs");
const floorMap = document.querySelector("#floorMap");
const bookingList = document.querySelector("#bookingList");
const floorTitle = document.querySelector("#floorTitle");
const floorSubtitle = document.querySelector("#floorSubtitle");
const buildingLabel = document.querySelector("#buildingLabel");
const freeCount = document.querySelector("#freeCount");
const busyCount = document.querySelector("#busyCount");
const dialog = document.querySelector("#bookingDialog");
const form = document.querySelector("#bookingForm");
const formError = document.querySelector("#formError");
const selectedBedTitle = document.querySelector("#selectedBedTitle");
const selectedBedKicker = document.querySelector("#selectedBedKicker");
const toast = document.querySelector("#toast");

const floors = window.FLOORS;

function floorById(id) {
  return floors.find((floor) => floor.id === id);
}

function bedById(id) {
  for (const floor of floors) {
    const bed = floor.beds.find((item) => item.id === id);
    if (bed) return { bed, floor };
  }
  return null;
}

async function loadBookings() {
  const response = await fetch("/api/bookings");
  const data = await response.json();
  state.bookings = new Map(data.bookings.map((booking) => [booking.bed_id, booking]));
  renderAll();
}

function renderAll() {
  renderFloorTabs();
  renderFloor();
  renderBookings();
  renderStats();
}

function renderFloorTabs() {
  const availableFloors = floors.filter((floor) => floor.building === state.building);
  if (!availableFloors.some((floor) => floor.id === state.floorId)) {
    state.floorId = availableFloors[0].id;
  }

  floorTabs.innerHTML = "";
  for (const floor of availableFloors) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `floor-tab ${floor.id === state.floorId ? "active" : ""}`;
    button.textContent = `Этаж ${floor.floor}`;
    button.dataset.floor = floor.id;
    button.addEventListener("click", () => {
      state.floorId = floor.id;
      renderAll();
    });
    floorTabs.append(button);
  }
}

function renderFloor() {
  const floor = floorById(state.floorId);
  buildingLabel.textContent = floor.buildingName;
  floorTitle.textContent = floor.title;
  floorSubtitle.textContent = floor.subtitle;
  floorMap.style.setProperty("--ratio", `${floor.canvas.width} / ${floor.canvas.height}`);
  floorMap.innerHTML = "";

  for (const room of floor.rooms) {
    const el = document.createElement("div");
    el.className = "room";
    place(el, room);
    el.innerHTML = `<span>${room.label}</span>`;
    floorMap.append(el);
  }

  for (const wall of floor.walls || []) {
    const el = document.createElement("div");
    el.className = "wall";
    place(el, wall);
    floorMap.append(el);
  }

  for (const bed of floor.beds) {
    const isBusy = state.bookings.has(bed.id);
    const button = document.createElement("button");
    button.type = "button";
    button.className = `bed ${bed.orientation} ${isBusy ? "busy" : "free"}`;
    button.dataset.bed = bed.id;
    button.disabled = isBusy;
    button.setAttribute("aria-label", isBusy ? `${bed.label} занято` : `${bed.label} свободно`);
    if (bed.note) {
      button.title = bed.note;
    }
    place(button, bed);

    const booking = state.bookings.get(bed.id);
    button.innerHTML = `
      <span class="bed-frame"></span>
      <span class="mattress"></span>
      <span class="blanket"></span>
      <span class="pillow"></span>
      <span class="bed-label">${isBusy ? escapeHtml(booking.name) : bed.label}</span>
      ${bed.note ? `<span class="bed-note">${escapeHtml(bed.note)}</span>` : ""}
    `;
    button.addEventListener("click", () => openBookingDialog(bed, floor));
    floorMap.append(button);
  }
}

function place(el, item) {
  el.style.left = `${item.x}%`;
  el.style.top = `${item.y}%`;
  el.style.width = `${item.w}%`;
  el.style.height = `${item.h}%`;
}

function renderBookings() {
  const bookings = [...state.bookings.values()];
  if (!bookings.length) {
    bookingList.innerHTML = `<p class="empty">Пока все места свободны.</p>`;
    return;
  }

  bookingList.innerHTML = "";
  for (const booking of bookings) {
    const meta = bedById(booking.bed_id);
    const item = document.createElement("article");
    item.className = "booking-item";
    item.innerHTML = `
      <div class="booking-copy">
        <strong>${escapeHtml(booking.name)}</strong>
        <span>${meta.floor.title}, ${meta.bed.label}</span>
        ${booking.comment ? `<p>${escapeHtml(booking.comment)}</p>` : ""}
      </div>
      <button class="checkout-button" type="button" data-checkout="${booking.bed_id}">Выписаться</button>
    `;
    bookingList.append(item);
  }
}

function renderStats() {
  const total = floors.reduce((sum, floor) => sum + floor.beds.length, 0);
  const busy = state.bookings.size;
  freeCount.textContent = total - busy;
  busyCount.textContent = busy;
}

function openBookingDialog(bed, floor) {
  state.selectedBed = bed;
  form.reset();
  formError.textContent = "";
  selectedBedKicker.textContent = floor.title;
  selectedBedTitle.textContent = `Забронировать ${bed.label}`;
  dialog.showModal();
  form.elements.name.focus();
}

async function submitBooking(event) {
  event.preventDefault();
  if (!state.selectedBed) return;

  const submitButton = form.querySelector(".submit-button");
  submitButton.disabled = true;
  formError.textContent = "";

  const payload = {
    bed_id: state.selectedBed.id,
    name: form.elements.name.value,
    contact: form.elements.contact.value,
    comment: form.elements.comment.value,
  };

  try {
    const response = await fetch("/api/bookings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Не получилось забронировать место.");
    }

    state.bookings.set(data.booking.bed_id, data.booking);
    dialog.close();
    renderAll();
    showToast(data.message);
  } catch (error) {
    formError.textContent = error.message;
  } finally {
    submitButton.disabled = false;
  }
}

async function checkoutBed(bedId) {
  const booking = state.bookings.get(bedId);
  if (!booking) return;

  try {
    const response = await fetch(`/api/bookings/${encodeURIComponent(bedId)}`, {
      method: "DELETE",
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "Не получилось выписаться.");
    }

    state.bookings.delete(bedId);
    renderAll();
    showToast(data.message);
  } catch (error) {
    showToast(error.message);
  }
}

function showToast(message) {
  toast.textContent = message;
  toast.classList.add("visible");
  window.setTimeout(() => toast.classList.remove("visible"), 3600);
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.querySelectorAll("[data-building]").forEach((button) => {
  button.addEventListener("click", () => {
    state.building = button.dataset.building;
    document.querySelectorAll("[data-building]").forEach((item) => {
      item.classList.toggle("active", item === button);
    });
    renderAll();
  });
});

document.querySelector("#refreshButton").addEventListener("click", loadBookings);
document.querySelector("#closeDialog").addEventListener("click", () => dialog.close());
bookingList.addEventListener("click", (event) => {
  const button = event.target.closest("[data-checkout]");
  if (!button) return;
  checkoutBed(button.dataset.checkout);
});
form.addEventListener("submit", submitBooking);

loadBookings().catch(() => {
  showToast("Не удалось загрузить брони. Проверьте сервер.");
  renderAll();
});
