#!/usr/bin/env python3

from flask import Flask, render_template
import base64

app = Flask(__name__)

# cmd;rarity;history;execs;rank;arg_density;redirect_rate;mastery;flavor
# 0    1     2       3     4     5             6           7        8

@app.route("/card/<string:b64_card>")
def card_view(b64_card):
    decoded_text = base64.b64decode(b64_card).decode("utf-8")
    parts = decoded_text.split(";")

    info = {
        "cmd": parts[0],
        "rarity": parts[1],
        "history": parts[2],
        "execs": parts[3],
        "rank": parts[4],
        "arg_density": parts[5],
        "redirect_rate": parts[6],
        "mastery": parts[7],
        "flavor": parts[8]
    }

    return render_template("card.html.j2", info=info, b64_card=b64_card)
