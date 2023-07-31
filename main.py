from aiogram import Bot, Dispatcher, types, executor
import random

# Колода карт
deck = []


user_data = {}

# Карты и их количества
numeric_cards = [4, 6, 8, 10, 12, 14, 16, 18]
picture_cards = ['L', 'L', 'L', 'L', 'G', 'G', 'G', 'G']
hunter_card = ['H', 'H', 'H']
ace_cards = [2, 2, 11, 11]
twenty_card = ['20']

# Количество карт для раздачи каждому игроку
cards_per_player = 4

# Команды бота
commands = {
    "start": "Присоединиться к игре",
    "play": "Сделать ход",
}

# Создаем бота и диспетчера
bot = Bot(token="5941637466:AAF-jDZVa0-3w7J7mALmNTB1sgiZB1EdES8")
dp = Dispatcher(bot)



# Функция для создания и перемешивания колоды
def create_deck():
    global deck
    deck = numeric_cards * 3 + picture_cards * 3 + hunter_card + ace_cards * 2 + twenty_card
    random.shuffle(deck)

# Функция для раздачи карт игроку и дилеру
def deal_cards(user_id):
    player_hand = []
    dealer_hand = []

    for _ in range(cards_per_player):
        if len(deck) > 0:
            card = deck.pop(0)
            player_hand.append(card)
            user_data[user_id].append(card)
    return player_hand, dealer_hand

# Функция для определения победителя и подсчет очков
def calculate_scores(player_hand, dealer_hand):
    player_score = 0
    dealer_score = 0

    # Добавляем очки за победу по наибольшему количеству выигранных карт
    max_player_cards = max(player_hand.count(card) for card in set(player_hand))
    max_dealer_cards = max(dealer_hand.count(card) for card in set(dealer_hand))
    if max_player_cards >= max_dealer_cards:
        player_score += 2
    else:
        dealer_score += 2

    # Добавляем очки за победу по наибольшему количеству выигранных трефовых карт
    player_tref_cards = player_hand.count('H')
    dealer_tref_cards = dealer_hand.count('H')
    if player_tref_cards >= dealer_tref_cards:
        player_score += 1
    else:
        dealer_score += 1

    # Добавляем очки за выигрыш червового туза
    if 11 in player_hand:
        player_score += 1
    elif 11 in dealer_hand:
        dealer_score += 1

    # Добавляем очки за выигрыш бубновой 20
    if '20' in player_hand:
        player_score += 1
    elif '20' in dealer_hand:
        dealer_score += 1

    return player_score, dealer_score

# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    user_id = message.from_id
    if user_id not in user_data:
        user_data[user_id]=[]

    create_deck()

    player_hand, dealer_hand = deal_cards(user_id)

    player_hand_str = " ".join(str(player_hand))
    await message.answer(f"Ваша рука: {player_hand_str}\n\nВведите команду /play, чтобы сделать ход.")

    # Сохраняем данные руки игрока и дилера в состояние пользователя
    await dp.storage.set_data(user=message.from_id, data={"player_hand": player_hand, "dealer_hand": dealer_hand})
    

# Обработчик команды /play
@dp.message_handler(commands=['play'])
async def play(message: types.Message):
    # Получаем данные руки игрока и дилера из состояния пользователя
    data = await dp.storage.get_data(user=message.from_id)
    player_hand = data.get("player_hand", [])
    dealer_hand = data.get("dealer_hand", [])

    if not player_hand or not dealer_hand:
        await message.answer("Игра не начата. Введите команду /start, чтобы начать игру.")
        return

    player_score, dealer_score = calculate_scores(player_hand, dealer_hand)

    await message.answer(f"Ваша рука: {' '.join(player_hand)}\nРука дилера: {' '.join(dealer_hand)}")
    await message.answer(f"Ваши очки: {player_score}\nОчки дилера: {dealer_score}")

    # Очищаем состояние пользователя
    await dp.storage.reset_data(user=message.from_user.id)

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
