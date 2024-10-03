# Telegram Bot @kumaxim-bot

Если вы используйте IDE JetBrains PyCharm, то вам понадобится добавить в глобальные исключения следующий файл
https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore

Для этого скачайте его и положите, например, в корневую директорию текущего пользователя:
```shell
mv -v JetBrains.gitignore ~/.jetbrains.gitignore
```

Затем, необходимо добавить его в глобальный `.gitconfig`, выполнив
```shell
git config --global core.excludesFile '~/.jetbrains.gitignore'
```

Аналогичные файлы для других IDE можно найти в репозитории [github/gitignore](https://github.com/github/gitignore)