from django.urls import reverse
from model_bakery.baker import make
import pytest
from rest_framework import status

from apps.locations.models import City
from apps.reviews.models import Review
from apps.sites.models import Site, BaseSite, SiteAudio, SiteImage
from apps.tours.models import SharedPrivateTour, UserTour, Tour, TourSite
from apps.users.models import User
from apps.utils.tests_query_counter import APIClientWithQueryCounter


class TestGetTours:
    def test_get_tours_returns_tours(self, client: APIClientWithQueryCounter, single_tour, expected_tour_data):
        path = reverse("tours-detail", args=[single_tour.id])
        response = client.get(path)

        assert response.status_code == status.HTTP_200_OK, response.json()

        expected_tour_data.pop("rating")
        assert expected_tour_data == response.json()

    def test_get_not_existing_tour_returns_not_found(self, client: APIClientWithQueryCounter):
        not_existing_tour_id = 100
        path = reverse("tours-detail", args=[not_existing_tour_id])
        response = client.get(path)

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    @pytest.mark.parametrize("is_approved,is_enabled", [(True, False), (False, True), (False, False)])
    def test_retrieve_tours_returns_only_approved_and_enabled_tours(
        self, client: APIClientWithQueryCounter, single_tour: Tour, is_approved, is_enabled
    ):
        tour = make(Tour, is_approved=is_approved, is_enabled=is_enabled)
        response = client.get(reverse("tours-detail", args=[tour.id]))
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    def test_get_tours_response_includes_reviews(
        self, user, client: APIClientWithQueryCounter, single_tour, expected_tour_data_with_1_review
    ):
        review = Review.objects.create(tour=single_tour, reviewer=user, text="some text with over 20 symbols", rating=5)
        path = reverse("tours-detail", args=[single_tour.id])
        response = client.get(path)
        # adding these as quick fix since the id's were hardcoded in.
        expected_tour_data_with_1_review["reviews"][0]["id"] = review.id
        expected_tour_data_with_1_review["reviews"][0]["reviewer"] = user.id
        assert expected_tour_data_with_1_review == response.json()

    def test_tour_returns_first_site_image(self, client: APIClientWithQueryCounter):
        site_image_1 = make(SiteImage, image="first_tour_test_image.jpg")
        site_image_2 = make(SiteImage, image="second_tour_test_image.jpg")
        tour_with_image = make(Tour, is_approved=True, is_enabled=True)
        make(TourSite, site__base_site=site_image_1.base_site, tour=tour_with_image, order=0)
        make(TourSite, site__base_site=site_image_2.base_site, tour=tour_with_image, order=1)

        response = client.get(reverse("tours-detail", args=[tour_with_image.id]), query_limit=7)

        assert response.json().get("image", None) == "http://testserver/media/first_tour_test_image.jpg"


class TestBuyTour:
    def test_unauthenticated_client_cannot_buy_tour(self, client: APIClientWithQueryCounter, single_tour: Tour):
        response = client.post(reverse("tours-buy", args=[single_tour.id]))

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()

    def test_non_existing_tour_returns_not_found(self, authorized_client: APIClientWithQueryCounter):
        response = authorized_client.post(reverse("tours-buy", args=[100]))
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    def test_cannot_buy_already_owned_tour(
        self,
        authorized_client: APIClientWithQueryCounter,
        single_tour: Tour,
        user: User,
    ):
        UserTour.objects.create(tour=single_tour, user=user, price=single_tour.price)
        response = authorized_client.post(reverse("tours-buy", args=[single_tour.id]))

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json()["non_field_errors"][0] == "error_tour_already_owned"

    @pytest.mark.parametrize("balance_difference", [(0, None), (1, None)])
    def test_tour_bought_successfully(
        self,
        authorized_client: APIClientWithQueryCounter,
        single_tour: Tour,
        user: User,
        expected_tour_data: dict,
        balance_difference: tuple,
    ):
        user.balance = single_tour.price + balance_difference[0]
        user.save(update_fields=["balance"])
        response = authorized_client.post(reverse("tours-buy", args=[single_tour.id]), query_limit=7)
        assert response.status_code == status.HTTP_201_CREATED, response.json()

        # Check UserTour created in db
        user_tour_from_db = UserTour.objects.filter(tour__id=single_tour.id).first()
        assert user_tour_from_db is not None
        assert user_tour_from_db.tour == single_tour
        assert user_tour_from_db.user == user
        assert user_tour_from_db.price == single_tour.price
        assert user_tour_from_db.status == "New"

        # Check if user balance was updated
        user.refresh_from_db()
        assert user.balance == balance_difference[0]

        expected_tour_data.pop("reviews", None)
        expected_tour_data.pop("sites", None)  # Tour will be serialized without sites
        expected_response_payload = {
            "id": user_tour_from_db.id,
            "created_at": user_tour_from_db.created_at.strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
            "price": single_tour.price,
            "status": "New",
            "is_finished_once": False,
            "tour": expected_tour_data,
        }
        assert response.json() == expected_response_payload

    def test_tour_price_greater_than_user_balance_response(
        self,
        authorized_client: APIClientWithQueryCounter,
        single_tour: Tour,
        user: User,
    ):
        user.balance = 1
        user.save(update_fields=["balance"])
        single_tour.price = 10
        single_tour.save(update_fields=["price"])
        response = authorized_client.post(reverse("tours-buy", args=[single_tour.id]))

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json()["non_field_errors"][0] == "error_wallet_balance_less_than_tour_price"


class TestTourFilterByCity:
    def test_filter_tours_by_city_id(self, client: APIClientWithQueryCounter, tours_list, expected_tours):
        path = reverse("city-tours", args=[5])
        response = client.get(path, query_limit=7)

        assert response.status_code == status.HTTP_200_OK, response.json()

        assert expected_tours == response.json()["results"]

    def test_filter_tours_by_nonexistent_city_id(self, client: APIClientWithQueryCounter, tours_list):
        path = reverse("city-tours", args=[100000])
        response = client.get(path)

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


class TestCreateTourEndpoint:
    def test_unauthenticated_user_cannot_create_tour(
        self, client: APIClientWithQueryCounter, create_tour_request_data: dict
    ):
        response = client.post(reverse("tours-list"), data=create_tour_request_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()

    def test_cannot_create_tour_with_unapproved_site(
        self, authorized_client: APIClientWithQueryCounter, create_tour_request_data: dict
    ):
        unapproved_site = Site.objects.get(id=create_tour_request_data["sites_ids_ordered"][0])
        unapproved_site.is_approved = False
        unapproved_site.save(update_fields=["is_approved"])

        response = authorized_client.post(reverse("tours-list"), data=create_tour_request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json()["non_field_errors"][0] == "error_not_all_sites_are_approved"

    def test_cannot_create_tour_with_non_unique_site_ids(
        self, authorized_client: APIClientWithQueryCounter, create_tour_request_data: dict
    ):
        create_tour_request_data["sites_ids_ordered"][0] = create_tour_request_data["sites_ids_ordered"][1]

        response = authorized_client.post(reverse("tours-list"), data=create_tour_request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json()["non_field_errors"][0] == "error_site_ids_non_unique"

    def test_cannot_create_tour_with_different_site_city(
        self, authorized_client: APIClientWithQueryCounter, create_tour_request_data: dict
    ):
        site_with_changed_city = BaseSite.objects.get(site__id=create_tour_request_data["sites_ids_ordered"][0])
        site_with_changed_city.city = make(City)
        site_with_changed_city.save(update_fields=["city"])

        response = authorized_client.post(reverse("tours-list"), data=create_tour_request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json()["non_field_errors"][0] == "error_all_sites_not_in_same_city"

    def test_cannot_create_tour_with_different_site_languages(
        self, authorized_client: APIClientWithQueryCounter, create_tour_request_data: dict
    ):
        site_with_changed_language = Site.objects.get(id=create_tour_request_data["sites_ids_ordered"][0])
        site_with_changed_language.language = "LT"
        site_with_changed_language.save(update_fields=["language"])

        response = authorized_client.post(reverse("tours-list"), data=create_tour_request_data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert response.json()["non_field_errors"][0] == "error_sites_languages_not_same"

    def test_tour_created(self, authorized_client: APIClientWithQueryCounter, create_tour_request_data: dict):
        response = authorized_client.post(reverse("tours-list"), data=create_tour_request_data)
        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert Tour.objects.count() == 1

        created_tour_from_db = Tour.objects.first()
        created_tour_sites_ids = list(created_tour_from_db.sites.values_list("id", flat=True))

        expected_response_payload = {
            "id": created_tour_from_db.id,
            "language": create_tour_request_data["language"],
            "overview": create_tour_request_data["overview"],
            "title": create_tour_request_data["title"],
            "price": create_tour_request_data["price"],
            "source": create_tour_request_data["source"],
            "sites": list(
                Site.objects.filter(id__in=create_tour_request_data["sites_ids_ordered"]).values_list("id", flat=True)
            ),
            "is_audio": False,
            "is_private": False,
        }

        assert response.json() == expected_response_payload
        assert created_tour_sites_ids == expected_response_payload["sites"]
        assert created_tour_from_db.language == expected_response_payload["language"]
        assert created_tour_from_db.overview == expected_response_payload["overview"]
        assert created_tour_from_db.title == expected_response_payload["title"]
        assert created_tour_from_db.price == expected_response_payload["price"]
        assert created_tour_from_db.source == expected_response_payload["source"]
        assert created_tour_from_db.is_audio == expected_response_payload["is_audio"]

        # check if site order was assigned correctly
        tour_site_0 = TourSite.objects.get(site_id=create_tour_request_data["sites_ids_ordered"][0])
        tour_site_1 = TourSite.objects.get(site_id=create_tour_request_data["sites_ids_ordered"][1])
        tour_site_2 = TourSite.objects.get(site_id=create_tour_request_data["sites_ids_ordered"][2])
        assert tour_site_0.order == 0
        assert tour_site_1.order == 1
        assert tour_site_2.order == 2

    def test_audio_tour_flag_set_correct(
        self, authorized_client: APIClientWithQueryCounter, create_tour_request_data: dict
    ):
        make(SiteAudio, site_id=create_tour_request_data["sites_ids_ordered"][0])
        response = authorized_client.post(reverse("tours-list"), data=create_tour_request_data)

        assert response.status_code == status.HTTP_201_CREATED, response.json()

        created_tour_from_db = Tour.objects.filter(id=response.json()["id"]).first()

        assert created_tour_from_db.is_audio is True
        assert response.json()["is_audio"] is True

    def test_non_existing_site_id_response(
        self, authorized_client: APIClientWithQueryCounter, create_tour_request_data: dict
    ):
        create_tour_request_data["sites_ids_ordered"][0] = 100000
        response = authorized_client.post(reverse("tours-list"), data=create_tour_request_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
        assert response.json()["detail"] == "error_one_or_more_sites_do_not_exist"


class TestShareTour:
    def test_unauthenticated_user_can_not_share_tour(self, client: APIClientWithQueryCounter):
        path = reverse("tours-share", args=[100])
        response = client.post(path, data={})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()

    def test_non_existing_tour_returns_not_found(self, authorized_client: APIClientWithQueryCounter):
        path = reverse("tours-share", args=[100])
        share_data = {
            "receiver_email": "receiver@test.com",
        }
        response = authorized_client.post(path, data=share_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    def test_non_existing_user_email_returns_not_found(self, authorized_client: APIClientWithQueryCounter, single_tour):
        path = reverse("tours-share", args=[single_tour.id])
        share_data = {
            "receiver_email": "receiver@test.com",
        }
        response = authorized_client.post(path, data=share_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()

    def test_share_tour(self, authorized_client: APIClientWithQueryCounter, single_tour):
        path = reverse("tours-share", args=[single_tour.id])
        second_user = make(User)
        share_data = {
            "receiver_email": second_user.email,
        }

        response = authorized_client.post(path, data=share_data, query_limit=7)

        assert response.status_code == status.HTTP_201_CREATED, response.json()
        assert SharedPrivateTour.objects.count() == 1

        shared_tour = SharedPrivateTour.objects.first()

        assert shared_tour.user_tour.tour == single_tour
        assert shared_tour.user_tour.user.email == share_data["receiver_email"]
        assert shared_tour.shared_by == single_tour.author

    def test_can_not_share_not_your_created_tour(self, authorized_client: APIClientWithQueryCounter, single_tour):
        path = reverse("tours-share", args=[single_tour.id])
        second_user = make(User)
        tour_creator = make(User)
        single_tour.author = tour_creator
        single_tour.save()
        share_data = {
            "receiver_email": second_user.email,
        }

        response = authorized_client.post(path, data=share_data, query_limit=7)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert SharedPrivateTour.objects.count() == 0
        assert response.json()["non_field_errors"][0] == "error_current_user_does_not_own_this_tour"

    def test_can_not_share_tour_if_receiver_has_it(self, authorized_client: APIClientWithQueryCounter, single_tour):
        path = reverse("tours-share", args=[single_tour.id])
        second_user = make(User)
        make(UserTour, user=second_user, tour=single_tour)
        share_data = {
            "receiver_email": second_user.email,
        }

        response = authorized_client.post(path, data=share_data, query_limit=7)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert SharedPrivateTour.objects.count() == 0
        assert response.json()["non_field_errors"][0] == "error_tour_is_already_owned_by_user"

    def test_can_not_share_tour_to_current_user(self, authorized_client: APIClientWithQueryCounter, user, single_tour):
        path = reverse("tours-share", args=[single_tour.id])

        share_data = {
            "receiver_email": user.email,
        }

        response = authorized_client.post(path, data=share_data, query_limit=7)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert SharedPrivateTour.objects.count() == 0
        assert response.json()["non_field_errors"][0] == "error_can_not_share_a_tour_to_yourself"

    def test_can_not_share_not_private(self, authorized_client: APIClientWithQueryCounter, single_tour):
        path = reverse("tours-share", args=[single_tour.id])
        single_tour.is_private = False
        single_tour.save()

        second_user = make(User)
        share_data = {
            "receiver_email": second_user.email,
        }

        response = authorized_client.post(path, data=share_data, query_limit=7)

        assert response.status_code == status.HTTP_400_BAD_REQUEST, response.json()
        assert SharedPrivateTour.objects.count() == 0
        assert response.json()["non_field_errors"][0] == "error_can_share_only_private_tour"


class TestGetSharedTours:
    def test_unauthenticated_user_can_not_get_shared_tours(self, client: APIClientWithQueryCounter):
        path = reverse("current-user-tours-shared")
        response = client.get(path)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.json()

    def test_get_shared_tours(self, authorized_client: APIClientWithQueryCounter, user, tours_list, expected_tours):
        user_tour_one = make(UserTour, user=user, tour=tours_list[0])
        user_tour_two = make(UserTour, user=user, tour=tours_list[2])
        make(SharedPrivateTour, user_tour=user_tour_one)
        make(SharedPrivateTour, user_tour=user_tour_two)

        path = reverse("current-user-tours-shared")
        response = authorized_client.get(path, query_limit=7)

        assert response.status_code == status.HTTP_200_OK, response.json()
        assert response.json()["results"] == expected_tours
