from .models import User, ReferralCodeModel, GoldUsersListModel, PointWalletModel, NormalUsersListModel, AmountModel, WithDrawalRequestModel, RefMoneyModel
from django.db import transaction
from decimal import Decimal
def process_referral_signup(new_user, referral_code):
    with transaction.atomic():
        print("Processing referral signup for new user:", new_user, "with referral code:", referral_code)
        try:
            referral_code_obj = ReferralCodeModel.objects.get(ref_code=referral_code)
            referrer = referral_code_obj.user
            print("Referrer found:", referrer)

            # Check if the referrer is a Gold user
            if GoldUsersListModel.objects.filter(user=referrer).exists():
                print("Referrer is a Gold user:", referrer)
                real_amount = AmountModel.objects.first()
                RefMoneyModel.objects.create(user=new_user,for_user=referrer,balance=real_amount.amount)
                new_user_normal_obj, created = NormalUsersListModel.objects.get_or_create(user=new_user)
                new_user_normal_obj.parent.add(referrer)
                assign_to_level(new_user, referrer, 1)

            # Check if the referrer's referrer is a Gold user
            elif ReferralCodeModel.objects.filter(user=referrer).exists() and \
                GoldUsersListModel.objects.filter(user=ReferralCodeModel.objects.get(user=referrer).referrer).exists():
                grand_referrer = ReferralCodeModel.objects.get(user=referrer).referrer
                print("grand referrer for level 2: ", grand_referrer)
                if grand_referrer and GoldUsersListModel.objects.filter(user=grand_referrer).exists():
                    normal_user_list, created = NormalUsersListModel.objects.get_or_create(user=referrer)
                    normal_user_list.users.add(new_user)
                    new_user_normal_obj, created = NormalUsersListModel.objects.get_or_create(user=new_user)
                    new_user_normal_obj.parent.add(normal_user_list.user)
                    real_amount = AmountModel.objects.first()
                    wallet, created = PointWalletModel.objects.get_or_create(user=referrer)
                    if wallet.balance != Decimal('0.0'):
                        wallet.balance += real_amount.amount
                    else:
                        wallet.balance += float(real_amount.amount)
                    RefMoneyModel.objects.create(user=new_user,for_user=referrer,balance=real_amount.amount)
                    wallet.save()
                    print("Added to NormalUsersListModel:", referrer)

                    print("Grand referrer is a Gold user:", grand_referrer)
                    assign_to_level(new_user, grand_referrer, 2)
                else:
                    print('the grand referrer for level 2 is not gold obv')
            # Check if the referrer's referrer is under a Gold user
            elif ReferralCodeModel.objects.filter(user=referrer).exists():
                print('in the level 3 tree')
                normal_user_list, created = NormalUsersListModel.objects.get_or_create(user=referrer)
                normal_new_user_list, created = NormalUsersListModel.objects.get_or_create(user=new_user)
                normal_new_user_list.parent.add(normal_user_list.user)
                normal_user_list.users.add(normal_new_user_list.user)
                real_amount = AmountModel.objects.first()
                wallet, created = PointWalletModel.objects.get_or_create(user=referrer)
                if wallet.balance != Decimal('0.0'):
                    wallet.balance += real_amount.amount
                else:
                    wallet.balance += float(real_amount.amount)
                RefMoneyModel.objects.create(user=new_user,for_user=referrer,balance=real_amount.amount)
                wallet.save()
                print('normal user referrer obj: ' ,normal_user_list.user)

                parent_referrer = normal_user_list.parent.first()
                print('Parent referrer object:', parent_referrer)
                if parent_referrer != None:
                    parent_parent_referrer = NormalUsersListModel.objects.get(user=parent_referrer)
                    print('Parent of parent referrer:', parent_parent_referrer.parent.all())
                    parent_of_parent_referrer_qs = parent_parent_referrer.parent.all()
                    if parent_of_parent_referrer_qs.exists():
                        parent_of_parent_referrer = parent_of_parent_referrer_qs.first()
                        print('Parent of Parent Referrer User:', parent_of_parent_referrer)
                        if parent_of_parent_referrer and GoldUsersListModel.objects.filter(user=parent_of_parent_referrer).exists():
                            gold_referrer = GoldUsersListModel.objects.get(user=parent_of_parent_referrer)

                            print("Referrer's referrer is a Gold user:", gold_referrer.user)
                            print(normal_user_list)
                            if gold_referrer.level_3 != normal_user_list:
                                pass
                            assign_to_level(new_user, gold_referrer.user, 3)
                        elif normal_user_list and not GoldUsersListModel.objects.filter(user=parent_referrer).exists():
                            print("No Gold")
                    else:
                        print("No Parent of Parent Referrer found.")
                else:
                    print("Parent referrer not found in NormalUsersListModel")
                
                
                    # reward_user(normal_user_list, 5)
            else:
                print('none of the above')
        except ReferralCodeModel.DoesNotExist:
            print("Invalid referral code:", referral_code)


def assign_to_level(new_user, gold_user, level):
    print("Assigning user:", new_user, "to level", level, "under gold user:", gold_user)
    gold_user_list = GoldUsersListModel.objects.get(user=gold_user)
    real_amount = AmountModel.objects.first()

    if level == 1:
        gold_user_list.level_1.add(new_user)
    elif level == 2:
        RefMoneyModel.objects.create(user=new_user,for_user=gold_user,balance=real_amount.amount)
        gold_user_list.level_2.add(new_user)
    elif level == 3:
        gold_user_list.level_3.add(new_user)
        RefMoneyModel.objects.create(user=new_user,for_user=gold_user,balance=real_amount.amount)

    print("User assigned to level", level)

    # Reward the gold user
    reward_user(gold_user, 5)
    print("Gold user rewarded:", gold_user)

def reward_user(user, amount):
    real_amount = AmountModel.objects.first()
    print("Rewarding user:", user, "with amount:", real_amount.amount)
    wallet, created = PointWalletModel.objects.get_or_create(user=user)
    wallet.balance += real_amount.amount
    wallet.save()
    print("User rewarded. New balance:", wallet.balance)
