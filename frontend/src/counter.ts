export function setupCounter(element: HTMLButtonElement) {
  const initCounter = async () => {

    const result = await fetch("http://localhost:8000/count", {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(responses => responses.json());

    element.innerHTML = `count is ${result.count}`;
  }

  const updateCounter = async () => {

    const result = await fetch("http://localhost:8000/count", {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
      },
    }).then(responses => responses.json());

    element.innerHTML = `count is ${result.count}`;
  }

  element.addEventListener('click', () => updateCounter());

  initCounter();
}
