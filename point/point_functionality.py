from .models import User, ReferralCodeModel, GoldUsersListModel

def process_referral_signup(new_user, referral_code):
    print("Processing referral signup for new user:", new_user, "with referral code:", referral_code)
    try:
        # Get the referrer's profile using the referral code
        referrer_profile = ReferralCodeModel.objects.get(ref_code=referral_code)
        referrer = referrer_profile.user
        print("Referrer found:", referrer)

        # Traverse up to 2 levels up in the referral chain
        for level in range(1, 4):
            print("Checking level", level, "for user:", referrer)
            if GoldUsersListModel.objects.filter(user=referrer).exists():
                print("Gold user found at level", level, ": ", referrer)
                # Assign the new user to the correct level under the gold user
                assign_to_level(new_user, referrer, level)
                break
            # Get the next user in the chain by looking up their referral code
            try:
                next_referrer_code = ReferralCodeModel.objects.get(user=referrer)
                referrer = ReferralCodeModel.objects.get(ref_code=next_referrer_code.ref_code).user
                print("Next referrer in the chain:", referrer)
            except ReferralCodeModel.DoesNotExist:
                print("No further referrer found at level", level)
                break

    except ReferralCodeModel.DoesNotExist:
        print("Invalid referral code:", referral_code)

def assign_to_level(new_user, gold_user, level):
    print("Assigning user:", new_user, "to level", level, "under gold user:", gold_user)
    gold_user_list = GoldUsersListModel.objects.get(user=gold_user)
    if level == 1:
        gold_user_list.level_1.add(new_user)
    elif level == 2:
        gold_user_list.level_2.add(new_user)
    elif level == 3:
        gold_user_list.level_3.add(new_user)
    print("User assigned to level", level)

    # Reward the gold user
    reward_user(gold_user, 5)
    print("Gold user rewarded:", gold_user)

def reward_user(user, amount):
    print("Rewarding user:", user, "with amount:", amount)
    wallet, created = PointWalletModel.objects.get_or_create(user=user)
    wallet.balance += amount
    wallet.save()
    print("User rewarded. New balance:", wallet.balance)
