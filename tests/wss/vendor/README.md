# Вендоренные библиотеки (только для тестовой страницы стенда)

| Файл | Что | Лицензия |
|------|-----|----------|
| `jssip-3.13.9.min.js` | JsSIP 3.13.9 (npm) + зависимости, собрано esbuild 0.25.0 в один файл | MIT (`JsSIP-LICENSE.md`); зависимости debug, events, sdp-transform — MIT |

Сборка (воспроизводимо):

```bash
npm install jssip@3.13.9 esbuild@0.25.0
echo "window.JsSIP = require('jssip');" > entry.js
npx esbuild entry.js --bundle --minify --format=iife --target=es2019 --outfile=jssip-3.13.9.min.js
```

sha256: `97d109d583169f4f6112eeee9175775ee26ef95fb4df155816ceb570bfaffc09`
