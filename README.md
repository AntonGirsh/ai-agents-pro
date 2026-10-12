# Homework 1
# Тема набора: формула 1, сезоны 2025-2026.

Сбор данных: только из Википедии, собирал Qwen 3.8, я вручную всё проверил.

## Результат первичной проверки свежести:
записей: 40, проблем: 0

Sonnet без инструментов: 14 из 40 верно, 35%. Потрачено $0.062
критерий свежести НЕ пройден: не выше 20 процентов

  f1-03: Which team did Lewis Hamilton join for the 2025 Formula One season? -> Ferrari  
  f1-04: Who replaced Lewis Hamilton at Mercedes for the 2025 Formula One season? -> Kimi Antonelli (Andrea Kimi Antonelli)  
  f1-05: Which driver replaced Jack Doohan at Alpine starting from the Emilia Romagna Grand Prix in -> Franco Colapinto  
  f1-06: Which driver was demoted from Red Bull Racing to Racing Bulls after the Chinese Grand Prix -> Liam Lawson  
  f1-07: Which driver replaced Liam Lawson at Red Bull Racing starting from the Japanese Grand Prix -> Yuki Tsunoda  
  f1-08: Who won the season-opening Australian Grand Prix in 2025? -> Lando Norris  
  f1-10: Who won the main race at the Chinese Grand Prix in 2025? -> Oscar Piastri won the 2025 Chinese Grand  
  f1-12: Who won the Japanese Grand Prix in 2025? -> Max Verstappen won the 2025 Japanese Gra  
  f1-13: Who won the Bahrain Grand Prix in 2025? -> Oscar Piastri won the 2025 Bahrain Grand  
  f1-14: Who won the Saudi Arabian Grand Prix in 2025? -> Oscar Piastri won the 2025 Saudi Arabian  
  f1-17: Who won the Emilia Romagna Grand Prix in 2025? -> Max Verstappen won the 2025 Emilia Romag  
  f1-22: Who won the British Grand Prix in 2025? -> Lando Norris won the 2025 British Grand  
  f1-37: Which team did Isack Hadjar join for the 2026 Formula One season? -> Red Bull Racing  
  f1-39: Which team did Franco Colapinto join for a full season in 2026? -> Alpine  


Это очень интересный результат, который во многом характеризует мир Формулы 1: 
1. многие контракты либо известны, либо просматриваются заранее, до их заключения
2. Лидеры меняются медленно, а значит результаты гонок находятся в очень узком диапазоне, который позволяет сильной модели угадывать результаты.

  При замене угаданных вопросов поправил промпт сборки: предложил сконцетрироваться на других типах событий, например поул-позициях и местах на подиуме.

## Попытка 2:
  записей: 41, проблем: 0

Sonnet без инструментов: 3 из 41 верно, 7%. Потрачено $0.071
критерий свежести пройден

  f1-13: What specific car part breach led to Lewis Hamilton's disqualification from the 2025 Chine -> Hamilton was disqualified due to excessi  
  f1-04: Who became the new Formula One championship leader after winning the 2025 Saudi Arabian Gr -> Oscar Piastri  
  f1-41: Who finished third at the 2025 Bahrain Grand Prix behind Oscar Piastri and George Russell? -> Lando Norris  

## Результат прогона
![alt text](image-1.png)

Основной вывод: да, тезис курса подтвердился. Слабая модель с полным набором инструментов показывает результат сильно лучший, чем сильная без инструментов и сопоставима с сильной моделью с неполным набором инструментов.

### Причины ошибок gpt-4o-mini(анализ трейсов)

### f1-03
в источнике использовалось слово "beached", а в запросе агента было "stuck in the grass". Буквального совпадения не было и агент не справился. Тут бы спас семантический поиск.

### f1-04
модель несколько раз пробовала отправлять новые запросы, запуталась в формулировках и в итоге вообще сгалюцинировала, т.к. в последнем тексте не было ответа на поставленный вопрс.
Тут классная эволюция поиска:
"2025 Saudi Arabian Grand Prix Formula One championship leader"  
"2025 Saudi Arabian Grand Prix winner"  
\"title\":\"Saudi Arabian Grand Prix\",\"keywords\":\"2025 winner, Formula One championship leader\"  
"2025 Saudi Arabian Grand Prix results" - в этой точке ещё и откат к web_search  
"2025 Formula One championship standings"  
тут модель будто вообще забывает изначальный вопрос и выдает финальный ответ, чтобы хоть что-то ответить  

### f1-04
искомая инфомация была лишь в 6-й ссылке. А мы подбираем лишь первую страницу  
Вообще, я так понял, это главная проблема ля большинства вопросов.

## прочее
Ну и часть проблем может быть связана с тем, что в коде с семинара была ошибка в функции web_search, которую я благополучно скопировал и увидел проблему только после прогона:  
В функции: "explainttext": 1, "exinro": 1  
Правильно: "explaintext": 1, "exintro": 1  
В результате приходит больший кусок текста и html, что может снижать качество ответа слабых моделей.



# Homework 2
## корпус текстов
корпус текстов изначально тот же самый, что и в дз1. Однако в процессе тестов по нему были серьёзные проблемы и пришлось его немного модифицировать.
В дз использовался Milvus Lite

## нарезка
изначально нарезка была по строкам и наивная по 400 символов. Обе показали очень низкое качество. В ходе анализ и экспериментов добавил наивную по 1200 символов и картина резка улучшилась, хотя по-прежнему 75% было потолком (см. график).

Анализ показал, что проблема в выбранных текстах: 27 страниц вики описывают большей частью гран-при формулы 1. Тексты стилистически и событийно однообразны: про одних и тех же людей пишут, как они побеждают, сходят с трассы и т.д. Без метаданных о том, о каком именно гран-при идет речь, очень легко ошибиться и принять одно событие за другое.

![alt text](img2.png)

## гибрид
| № | Нарезка | Поиск | Recall@1 | Recall@5 |
|:---:|:---|:---|:---:|:---:|
| 0 | по 400 символов | только вектор | 0.22 | 0.38 |
| 1 | по 400 символов | только слова | 0.22 | 0.45 |
| 2 | по 400 символов | гибрид RRF | 0.25 | 0.40 |
| 3 | по 1200 символов | только вектор | 0.62 | 0.72 |
| 4 | по 1200 символов | только слова | 0.32 | 0.68 |
| 5 | по 1200 символов | гибрид RRF | 0.60 | 0.70 |
| 6 | по строкам | только вектор | 0.32 | 0.40 |
| 7 | по строкам | только слова | 0.35 | 0.68 |
| 8 | по строкам | гибрид RRF | 0.35 | 0.65 |

![alt text](hybrid.png)

график подтверждает специфику корпуса: если ориентироваться на ключевые слова, то качество низкое. Более того, даже гибрид чуть хуже чистого вектора: слишком однообразная лексика в вопросах и ответах запутывает лексичекий поиск и этого достаточно, чтобы проседал общий скор.

# анализ провалов
провалов много.
- тип 1. ответ верный, но форма не на 100% совпадает с эталоном
- тип 2. ответ был в тексте, но модель его не нашла - 100% корреляция с силой модели
- тип 3. ответа не было в выбранных текстах - это беда нашео корпуса текстов, о которой я писал выше.

# выводы
- качество модели почти не влияет на качетво ответов с RAG
- стоимость ответов дешевой модели - 0.00007 (в прошлой теме - 0.00052) при более высокой точности. RAG рулит.

