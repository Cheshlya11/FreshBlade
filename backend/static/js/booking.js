const serviceCheckboxes = document.querySelectorAll('input[name="services"]');
const masterSelect = document.querySelector('select[name="master"]');
const datePicker = document.getElementById("date-picker");
const slotsContainer = document.getElementById("slots-container");
const startAtInput = document.getElementById("start_at");
const totalDurationEl = document.getElementById("total-duration");
const totalPriceEl = document.getElementById("total-price");

function updateSummary() {
  let duration = 0;
  let price = 0;
  serviceCheckboxes.forEach((cb) => {
    if (cb.checked) {
      duration += parseInt(cb.dataset.duration);
      price += parseFloat(cb.dataset.price);
    }
  });
  totalDurationEl.textContent = duration;
  totalPriceEl.textContent = price.toFixed(2);
  return duration;
}

async function loadSlots() {
  const masterId = masterSelect.value;
  const date = datePicker.value;
  const duration = updateSummary();

  startAtInput.value = "";
  slotsContainer.innerHTML = "";

  if (!masterId || !date || duration === 0) {
    slotsContainer.innerHTML =
      '<p class="subtitle">Select at least one service, a master and a date.</p>';
    return;
  }

  const response = await fetch(
    `/booking/available-slots/?master_id=${masterId}&date=${date}&duration=${duration}`,
  );
  const data = await response.json();

  if (!data.slots || data.slots.length === 0) {
    slotsContainer.innerHTML =
      '<p class="subtitle">No available times for this day.</p>';
    return;
  }

  data.slots.forEach((slot) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "slot-button";
    btn.textContent = slot.start;
    btn.addEventListener("click", () => {
      document
        .querySelectorAll(".slot-button")
        .forEach((b) => b.classList.remove("slot-button--selected"));
      btn.classList.add("slot-button--selected");
      startAtInput.value = slot.value;
    });
    slotsContainer.appendChild(btn);
  });
}

serviceCheckboxes.forEach((cb) => cb.addEventListener("change", loadSlots));
masterSelect.addEventListener("change", loadSlots);
datePicker.addEventListener("change", loadSlots);

updateSummary();
