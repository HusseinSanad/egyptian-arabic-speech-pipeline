import json
import yaml
import os
import random
from dotenv import load_dotenv
from google import genai
from utils import save_manifest


# -----------------------
# setup
# -----------------------
load_dotenv()

with open("configs/config.yaml", "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

seed = config.get("seed", 42)
random.seed(seed)

TOTAL = config.get("total_samples", 100)
USE_LLM = config.get("use_llm", False)

# -----------------------
# Gemini client
# -----------------------
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

# -----------------------
# templates
# -----------------------
TEMPLATES = {

    "casual_chat": [
        "انا {state} دلوقتي ومش عارف أركز خالص",
        "هو انت {question} ولا بتتكلم جد؟",
        "بص يا عم انا {action} ومش فاضي للكلام ده",
        "انا كنت {state} بس دلوقتي الوضع اتغير",
        "يعني انت شايف اني {reaction} كده ولا ايه",
        "بقولك ايه انا {state} من الصبح",
        "والله يا صاحبي انا {action} النهارده",
        "مش فاهم انت {question} ازاي بصراحة"
    ],

    "food_ordering": [
        "عايز اطلب {food} مع {drink} لو ينفع كده",
        "هاتلي {food} بس يكون سخن وطازة لو سمحت",
        "ممكن تبعتلي {food} بسرعة عشان انا جعان جدا",
        "عايز وجبة {food} ومعاها {drink} كبير",
        "نفسي اكل {food} من زمان",
        "هات {food} وكمان {drink} ساقع",
        "لو سمحت ابعتلي {food} قبل ما انام"
    ],

    "transportation": [
        "انا في الطريق دلوقتي بس الزحمة شغالة جامد",
        "هجيلك بعد {time} بس ممكن اتأخر شوية",
        "الطريق زحمة جدا ومش عارف اوصل بسرعة",
        "انا قريب منك بس واقف في زحمة صعبة",
        "العربية واقفة بقالها ساعة في الزحمة",
        "لسه فاضلي {time} واوصل",
        "الدنيا زحمة اوي النهارده"
    ],

    "code_switching": [
        "ابعتلي ال{english_word} بسرعة عشان محتاجه دلوقتي",
        "انا داخل call دلوقتي ومش هعرف ارد",
        "ابعتلي email او ال{english_word} لو جاهز",
        "مش لاقي ال{english_word} ممكن تساعدني",
        "بعتلك الfile بص عليه",
        "محتاج الlink ضروري حالاً",
        "خش الmeeting بسرعة"
    ],

    "football": [
        "الماتش كان {reaction} جدا ومفيهوش ملل خالص",
        "شوفت هدف {player} امبارح كان حاجة مش طبيعية",
        "الاهلي كان عامل ماتش {reaction} بصراحة",
        "الحكم كان {reaction} وده اثر على اللعب",
        "جون {player} قلب الماتش",
        "الدفاع كان {reaction} بصراحة",
        "الماتش امبارح كان تحفة"
    ],

    "emotions": [
        "انا {emotion} جدا ومش عارف اتعامل مع الموقف ده",
        "حاسس اني {state} ومحتاج اغير جو شوية",
        "الموضوع ده مخليني {emotion} ومش مرتاح خالص",
        "بصراحة انا {emotion} من اللي حصل",
        "مش قادر ابطل تفكير وحاسس اني {state}",
        "اليوم كان صعب وخلاني {emotion}"
    ],

    "work": [
        "الmeeting اتأجل ومش عارف امتى هيتحدد تاني",
        "بشتغل على الreport دلوقتي ومش فاضي خالص",
        "عندي call مهم بعد شوية ولازم اكون جاهز",
        "الشغل اليومين دول {state} جدا ومحتاج تركيز",
        "خلصت الtask بصعوبة النهارده",
        "الmanager طالب شغل كتير اوي",
        "اليوم كله meetings وصداع"
    ]
}

# -----------------------
# variables
# -----------------------
VARIABLES = {

    "state": [
        "زهقان جدا",
        "مضغوط في الشغل",
        "تايه شوية",
        "مركز بصعوبة",
        "مخنوق",
        "مرهق",
        "تعبان شوية"
    ],

    "question": [
        "فاهم اللي بيحصل",
        "وصلت للنقطة دي",
        "بتتكلم بجد",
        "حاسس باللي بقوله",
        "مستوعب الكلام",
        "بتفكر صح"
    ],

    "action": [
        "هتأخر شوية في الرد",
        "نازل دلوقتي من البيت",
        "مشغول جدا اليومين دول",
        "بحاول اخلص اللي ورايا",
        "مروق النهارده"
    ],

    "food": [
        "شاورما فراخ",
        "كشري كبير",
        "بيتزا مارجريتا",
        "برجر دوبل",
        "فراخ مشوية",
        "ساندوتش سجق"
    ],

    "drink": [
        "بيبسي ساقع",
        "عصير مانجا",
        "شاي بالنعناع",
        "قهوة ساقعة",
        "عصير برتقان"
    ],

    "time": [
        "10 دقايق",
        "ربع ساعة",
        "نص ساعة تقريباً",
        "20 دقيقة",
        "شوية صغيرين"
    ],

    "english_word": [
        "location",
        "email",
        "link",
        "file",
        "document",
        "meeting"
    ],

    "reaction": [
        "نار",
        "عظمة",
        "ممل شوية",
        "مش حلو خالص",
        "تحفة",
        "ضعيف"
    ],

    "player": [
        "زيزو",
        "الشحات",
        "امام عاشور",
        "كهربا",
        "عبدالله السعيد"
    ],

    "emotion": [
        "مبسوط",
        "مضايق",
        "متوتر",
        "قلقان",
        "مرتاح",
        "زعلان"
    ]
}

# -----------------------
# fill template
# -----------------------
def fill_template(template):

    for key, values in VARIABLES.items():

        placeholder = "{" + key + "}"

        if placeholder in template:
            template = template.replace(
                placeholder,
                random.choice(values)
            )

    return template


# -----------------------
# LLM refinement
# -----------------------
def refine_with_llm(text, domain):

    try:

        prompt = f"""
Rewrite this into natural spoken Egyptian Arabic.

Rules:
- Keep same meaning
- Egyptian dialect only
- One sentence only
- Max 15 words
- No explanations

Sentence:
{text}

Domain:
{domain}
"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        final_text = response.text.strip().replace("\n", " ")

        if len(final_text) > 0:
            return final_text

        return text

    except Exception:
        return text


# -----------------------
# detect code switching
# -----------------------
def detect_code_switching(text):

    return any(
        any(c.isascii() and c.isalpha() for c in word)
        for word in text.split()
    )


# -----------------------
# generate sample
# -----------------------
def generate_sample(idx):

    domain = random.choices(
        population=list(config["domain_weights"].keys()),
        weights=list(config["domain_weights"].values()),
        k=1
    )[0]

    template = random.choice(TEMPLATES[domain])

    filled = fill_template(template)

    # optional LLM usage
    if USE_LLM and random.random() < 0.3:
        final_text = refine_with_llm(filled, domain)
    else:
        final_text = filled

    return {
        "id": f"eg_{idx:04d}",
        "text": final_text,
        "domain": domain,
        "word_count": len(final_text.split()),
        "contains_code_switching": detect_code_switching(final_text)
    }


# -----------------------
# main
# -----------------------
def main():

    os.makedirs("data", exist_ok=True)

    output_file = config.get(
        "output_path",
        "data/prompts.jsonl"
    )

    print(f"Generating {TOTAL} samples...")

    seen = set()

    with open(output_file, "w", encoding="utf-8") as f:

        i = 1
        attempts = 0
        max_attempts = TOTAL * 50

        while i <= TOTAL and attempts < max_attempts:

            attempts += 1

            sample = generate_sample(i)

            # skip duplicates
            if sample["text"] in seen:
                continue

            seen.add(sample["text"])
            save_manifest(sample,stage="generated",
                          extra={"steps": {"generated": True}})

            f.write(
                json.dumps(sample, ensure_ascii=False) + "\n"
            )

            print(f"Generated {i}/{TOTAL}")

            i += 1

        if i <= TOTAL:
            print(f"Only generated {i-1} unique samples")

    print("Done ✔ prompts generated successfully")


if __name__ == "__main__":
    main()