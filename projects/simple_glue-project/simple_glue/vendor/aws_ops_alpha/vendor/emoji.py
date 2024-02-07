# -*- coding: utf-8 -*-

"""
Enumerate useful, UTF8 emoji characters.

- Full list is here: https://unicode.org/emoji/charts/full-emoji-list.html
- Emoji cheat sheet: https://github.com/ikatyang/emoji-cheat-sheet/blob/master/README.md
"""

__version__ = "0.1.1"


class Emoji:
    # start and end
    start_timer = "⏱"
    end_timer = "⏰"
    start = "⏯"
    end = "⏹"

    # Audio video symbol
    arrow_up_small = "🔼"
    arrow_down_small = "🔽"
    arrow_forward = "▶"
    arrow_backward = "◀"
    play_pause = "⏯"
    previous_track_button = "⏮"
    next_track_button = "⏭"
    repeat = "🔁"
    repeat_one = "🔂"
    shuffle = "🔀"
    stop_button = "⏹"
    eject_button = "⏏"
    arrow_double_up = "⏫"
    arrow_double_down = "⏬"
    cinema = "🎦"

    # logging
    debug = "🐞"
    info = "💬"
    warning = "❗"
    error = "🔥"
    critical = "💥"

    # status
    succeeded = "✅"
    failed = "❌"
    target = "🎯"
    in_progress = "⏳"
    stopp_sign = "🛑"
    no_entry = "🚫"

    # arrow
    arrow_up = "⬆"
    arrow_down = "⬇"
    arrow_left = "⬅"
    arrow_right = "➡"

    # hand
    point_left = "👈"
    point_right = "👉"
    point_up = "👆"
    point_down = "👇"
    thumb_up = "👍"
    thumb_down = "👎"

    # ci/cd action
    doc = "📔"
    test = "🧪"
    install = "💾"
    build = "🏗"
    fix = "🛠"
    deploy = "🚀"
    delete = "🗑"
    config = "⚙"
    container = "🥡"
    connect = "📶"

    # computer science
    thread = "🧵"
    file = "📄"
    folder = "📁"

    # AWS
    cloudformation = "🐑"
    awslambda = "λ"
    s3 = "🪣"

    # internet
    template = "📋"
    computer = "💻"
    package = "📦"
    email = "📫"
    factory = "🏭"
    label = "🏷"
    note = "📝"
    bulb = "💡"
    flash_light = "🔦"
    search = "🔍"
    printer = "🖨"
    battery = "🔋"
    electric_plug = "🔌"
    calendar = "📅"
    line_chart = "📈"
    bar_chart = "📊"

    # object
    shield = "🛡"
    ladder = "🪜"
    link = "🔗"
    screwdriver = "🪛"
    lock = "🔐"
    key = "🔑"
    pushpin = "📌"
    microscope = "🔬"
    bloom = "🧹"
    fire_extinguisher = "🧯"
    gem = "💎"
    pen = "🖋"
    money_bag = "💰"
    coin = "🪙"
    dollar = "💵"
    credit_card = "💳"

    # face expression
    happy_face = "😀"
    hot_face = "🥵"
    anger = "💢"
    eye = "👀"

    # ski & weather
    moon = "🌙"
    sunny = "🌤"
    star = "🌟"
    rain = "🌧"
    thunder = "🌩"
    tornado = "🌪"
    cyclone = "🌀"
    rainbow = "🌈"
    snow = "❄"
    zap = "⚡"

    # event
    halloween = "🎃"
    christmas_tree = "🎄"
    fireworks = "🎆"
    balloon = "🎈"
    sparkles = "✨"
    birthday = "🎂"
    gift = "🎁"
    tada = "🎉"

    # award
    trophy = "🏆"
    first_place = "🥇"
    second_place = "🥈"
    third_place = "🥉"
    medal = "🏅"

    # shape
    red_circle = "🔴"
    green_circle = "🟢"
    yellow_circle = "🟡"
    blue_circle = "🔵"

    red_square = "🟥"
    green_square = "🟩"
    yellow_square = "🟨"
    blue_square = "🟦"

    # programming language
    python = "🐍"

    # environment
    devops = "🛠"
    dev = "💻"
    sbx = "📦"
    tst = "🧪"
    stg = "🎸"
    qa = "👮"
    prd = "🏭"

    # aws codebuild
    install_phase = "🌱"
    pre_build_phase = "🌿"
    build_phase = "🍀"
    post_build_phase = "🌲"

    # human
    person = "👨"


if __name__ == "__main__":
    # make sure all the emoji are 1 character
    chars = list()
    for k, v in Emoji.__dict__.items():
        if not k.startswith("_"):
            if len(v) != 1:
                print(f"{k} = {v}, len = {len(v)}")

            # if len(v) == 1:
            chars.append(v)

    print(" ".join(chars))
