import './styles.css';

const games = [
  { name: 'WinGo', tag: '30 sec', colors: ['#f64b52', '#2ecc71', '#8b5cf6'] },
  { name: 'K3 Lottery', tag: 'Dice', colors: ['#ffb703', '#fb8500', '#ef476f'] },
  { name: '5D Lottery', tag: 'Fast', colors: ['#06b6d4', '#3b82f6', '#6366f1'] },
  { name: 'Aviator', tag: 'Crash', colors: ['#ef4444', '#111827', '#f59e0b'] },
];

const results = [
  ['202607100981', 'Green', '7'],
  ['202607100980', 'Red', '2'],
  ['202607100979', 'Violet', '0'],
  ['202607100978', 'Green', '9'],
];

document.querySelector('#games').innerHTML = games.map(game => `
  <article class="game-card">
    <div class="game-orbs" style="--a:${game.colors[0]};--b:${game.colors[1]};--c:${game.colors[2]}"><span></span><span></span><span></span></div>
    <div><h3>${game.name}</h3><p>${game.tag} rounds</p></div><button>Play</button>
  </article>`).join('');

document.querySelector('#results').innerHTML = results.map(([period, result, num]) => `<tr><td>${period}</td><td>${result}</td><td>${num}</td></tr>`).join('');

let seconds = 27;
setInterval(() => {
  seconds = seconds === 0 ? 29 : seconds - 1;
  document.querySelector('#timer').textContent = `00 : ${String(seconds).padStart(2, '0')}`;
}, 1000);
