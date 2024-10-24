import structlog
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandStart, CommandObject
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from fluent.runtime import FluentLocalization

# Declare router
router = Router()
router.message.filter(F.chat.type == "private")

# Declare logger
logger = structlog.get_logger()

# Declare handlers
@router.message(Command("start"))
async def cmd_owner_hello(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("hello-msg"))

# Donate
@router.message(Command("donate", "donat", "донат"))
async def donate(message: Message, command: CommandObject, l10n: FluentLocalization):
    # Check, if in command collect arguments value. Stars for donation
    # If not, then not complete the command and return message Error
    # Check value stars for donate if < 1 or > 2500, Error
    if command.args is None or not command.args.isdigit() or not 1 <= int(command.args) <= 2500:
        await message.answer(l10n.format_value("donate-input-error"))
        return
    
    amount = int(command.args)

    # Create keyboard
    kb = InlineKeyboardBuilder()
    kb.button(
        text=l10n.format_value("Donate", {"amount": amount}),
        pay=True, # REQUIRE!!!!
    )
    kb.button(
        text=l10n.format_value("Cancel"),
        callback_data="donate_cancel"
    )
    kb.adjust(1) # all buttons in 1 row
    # Formation INVOICE
    # For pay Telegram Stars sell list
    # MUST HAVE ONLY ONE ELEMENT
    prices = [LabeledPrice(label="XTR", amount=amount)] # TODO LabeledPrice(label="NOT", amount=amount)

    await message.answer_invoice(
        title=l10n.format_value("donate-invoice-title"),
        description=l10n.format_value("donate-invoice-description"),
        prices=prices,

        # provider_token must be empty
        provider_token="",

        # Any Data in payload
        payload=f"{amount}_stars",

        currency="XTR",

        reply_markup=kb.as_markup()
    )


@router.callback_query(F.data == "donate_cancel")
async def cancel_donate(callback: CallbackQuery, l10n: FluentLocalization):
    await callback.answer(l10n.format_value("donate-cencel-payment"))

    await callback.message.delete()

@router.message(Command("paysupport"))
async def support_donate(message: Message, l10n: FluentLocalization):
    await message.answer(l10n.format_value("donate-paysupport-message"))

@router.message(Command("refunds"))
async def cmd_refunds(message: Message, bot: Bot, command: CommandObject, l10n: FluentLocalization):
    # ID Transactions for refunds
    t_id = command.args

    if t_id is None:
        await message.answer(l10n.format_value("donate-refund-input-error"))
        return

    # try make refund
    try:
        pass
    except TelegramBadRequest as e:
        error = l10n.format_value("donate-refund-code-not-found")

        if "CHARGE_ALREADY_REFUNDED" in e.message:
            error = l10n.format_value("donate-refund-already-refunded")

        await message.answer(error)
        return

@router.pre_checkout_query()
async def pre_checkout_query(query: PreCheckoutQuery, l10n: FluentLocalization):
    # If we are sell items and answearing OK
    await query.answer(ok=True)

    # If we are not found item answearing not found
    # await query.answer(
    #     ok=False,
    #     error_message="Item is not found!"
    # )

@router.message(F.successfull_payment)
async def successfull_payment(message: Message, l10n: FluentLocalization):
    # payment SuccessFully Function
    await message.answer(
        l10n.format_value(
            "donate-successful-payment",
            {"t_id": message.successful_payment.telegram_payment_charge_id}
        ),

        # Add Message Effect
        message_effect_id="5104841245755180586",
        
        # fire - 5104841245755180586
        # like - 5107584321108051014
        # dislike - 5104858069142078462
        # hearts - 5159385139981059251
        # party - 5046509860389126442 
        # poop - 5046589136895476101
    )