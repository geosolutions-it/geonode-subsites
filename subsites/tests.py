from django.test import override_settings
from mock import MagicMock
from subsites.models import SubSite
from django.shortcuts import reverse
from geonode.base.models import GroupProfile, HierarchicalKeyword, Region, TopicCategory
from geonode.base.populate_test_data import create_single_dataset
from geonode.themes.models import GeoNodeThemeCustomization
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model


from subsites.views import bridge_view


class SubsiteTestCase(APITestCase):
    fixtures = [
        "initial_data.json",
        "group_test_data.json",
        "regions.json",
        "default_oauth_apps.json",
    ]

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls._create_keywords(cls)
        cls._create_themes(cls)
        cls._define_regions(cls)
        cls._define_groups(cls)
        cls._define_category(cls)
        cls._define_test_subsites(cls)
        cls._create_datasets(cls)

    def _create_keywords(cls):
        cls.keyword_hiking = HierarchicalKeyword.objects.create(
            path="hiking", name="hiking", slug="hiking", depth=1
        )
        cls.keyword_art = HierarchicalKeyword.objects.create(
            path="art", name="art", slug="art", depth=1
        )
        cls.keyword_sea = HierarchicalKeyword.objects.create(
            path="sea", name="sea", slug="sea", depth=1
        )

    def _define_category(cls):
        cls.category_environment = TopicCategory.objects.get(identifier="environment")
        cls.category_transportation = TopicCategory.objects.get(
            identifier="transportation"
        )

    def _define_regions(cls):
        cls.region_italy = Region.objects.get(name="Italy")
        cls.region_japan = Region.objects.get(name="Japan")

    def _define_groups(cls):
        cls.group_noob, _ = GroupProfile.objects.get_or_create(slug="noob")
        cls.group_expert, _ = GroupProfile.objects.get_or_create(slug="expert")

    def _create_themes(cls):
        cls.theme1 = GeoNodeThemeCustomization.objects.create(
            name="theme1",
            jumbotron_welcome_content="welcome_1",
        )

    def _define_test_subsites(cls):
        cls.subsite_sport, _ = SubSite.objects.get_or_create(
            slug="subsite_sport",
            theme=cls.theme1,
        )
        cls.subsite_sport.keyword.add(*[cls.keyword_hiking, cls.keyword_sea])
        cls.subsite_sport.region.add(cls.region_italy)
        cls.subsite_sport.groups.add(cls.group_noob)

        cls.subsite_other, _ = SubSite.objects.get_or_create(
            slug="subsite_other",
            theme=cls.theme1,
        )
        cls.subsite_other.keyword.add(
            *[cls.keyword_hiking, cls.keyword_art, cls.keyword_sea]
        )
        cls.subsite_other.region.add(cls.region_japan)
        cls.subsite_other.groups.add(*[cls.group_noob, cls.group_expert])
        cls.subsite_other.category.add(cls.category_transportation)

        cls.subsite_japan, _ = SubSite.objects.get_or_create(
            slug="subsite_japan",
            theme=cls.theme1,
        )
        cls.subsite_japan.keyword.add(*[cls.keyword_art])
        cls.subsite_japan.region.add(cls.region_japan)

        cls.subsite_regions, _ = SubSite.objects.get_or_create(
            slug="subsite_regions",
            theme=cls.theme1,
        )
        cls.subsite_regions.region.add(*[cls.region_italy, cls.region_japan])

        cls.subsite_transp, _ = SubSite.objects.get_or_create(
            slug="subsite_transp",
            theme=cls.theme1,
        )
        cls.subsite_transp.category.add(*[cls.category_transportation])

        cls.subsite_groups, _ = SubSite.objects.get_or_create(
            slug="subsite_groups",
            theme=cls.theme1,
        )
        cls.subsite_groups.groups.add(*[cls.group_noob, cls.group_expert])
        cls.subsite_groups.region.add(*[cls.region_italy, cls.region_japan])

        cls.subsite_datasets, _ = SubSite.objects.get_or_create(
            slug="subsite_dataset", theme=cls.theme1, types=["dataset"]
        )

        cls.subsite_geoapp, _ = SubSite.objects.get_or_create(
            slug="subsite_geoapp", theme=cls.theme1, types=["geoapp"]
        )

        cls.subsite_no_condition, _ = SubSite.objects.get_or_create(
            slug="subsite_no_condition",
            theme=cls.theme1,
        )

    def _create_datasets(cls):
        cls.hiking_dataset = create_single_dataset(
            name="hiking_dataset",
            keywords=[cls.keyword_hiking],
            group=cls.group_noob.group,
        )
        cls.hiking_dataset.regions.add(cls.region_italy)
        cls.hiking_dataset.save()

        cls.dataset_japan = create_single_dataset(
            name="japan_dataset",
            keywords=[cls.keyword_sea, cls.keyword_art],
        )
        cls.dataset_japan.regions.add(cls.region_japan)
        cls.dataset_japan.save()

        cls.japan_art_dataset = create_single_dataset(
            name="japan_art_dataset",
            keywords=[cls.keyword_art],
        )
        cls.japan_art_dataset.regions.add(cls.region_japan)
        cls.japan_art_dataset.save()

        cls.dataset_transp = create_single_dataset(
            name="dataset_transp",
        )
        cls.dataset_transp.category = cls.category_transportation
        cls.dataset_transp.save()

        cls.dataset_expert = create_single_dataset(
            name="dataset_expert",
            group=cls.group_expert.group,
        )
        cls.dataset_expert.regions.add(*[cls.region_italy, cls.region_japan])
        cls.dataset_expert.save()

        cls.dataset_noob = create_single_dataset(
            name="dataset_noob",
            group=cls.group_noob.group,
        )
        cls.dataset_noob.regions.add(*[cls.region_japan])
        cls.dataset_noob.save()

    """
    Pre -filter testcases
    """

    def test_subsite_sport(self):
        """
        Subsite sport:
            - keyword: keyword_sea, keyword_hiking
            - region: region_italy
            - group: group_noob
            - category: null
        Should match only: hiking_dataset
        """
        url = reverse("base-resources-list", args=[self.subsite_sport.slug])
        expected_total = 1
        expected_dataset = self.hiking_dataset
        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])
        self.assertEqual(expected_dataset.id, int(data["resources"][0]["pk"]))

    def test_subsite_japan(self):
        """
        Subsite Japan
            - keyword: keyword_art
            - region: region_japan
            - group: null
            - category: null
        Should match: japan_dataset, japan_art_dataset
        """
        url = reverse("base-resources-list", args=[self.subsite_japan.slug])
        expected_total = 2
        expected_datasets = [self.japan_art_dataset.id, self.dataset_japan.id]

        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])

        pk_in_data_response = [int(val["pk"]) for val in data["resources"]]

        self.assertListEqual(expected_datasets, pk_in_data_response)

    def test_subsite_regions(self):
        """
        Subsite regions
            - keyword: null
            - region: japan
            - group: null
            - category: null
        Should match: None
        """
        url = reverse("base-resources-list", args=[self.subsite_regions.slug])
        expected_total = 5

        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])

    def test_subsite_category(self):
        """
        Subsite subsite_transp
            - keyword: null
            - region: null
            - group: null
            - category: transportation
        Should match: dataset_transp
        """
        url = reverse("base-resources-list", args=[self.subsite_transp.slug])
        expected_total = 1
        expected_dataset = self.dataset_transp
        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])
        self.assertEqual(expected_dataset.id, int(data["resources"][0]["pk"]))

    def test_subsite_groups(self):
        """
        Subsite subsite_transp
            - keyword: null
            - region: italy, japan
            - group: noob, expert
            - category: null
        Should match: dataset_noob, dataset_expert, hiking_dataset
        """
        url = reverse("base-resources-list", args=[self.subsite_groups.slug])
        expected_total = 3
        expected_datasets = [
            self.dataset_noob.id,
            self.dataset_expert.id,
            self.hiking_dataset.id,
        ]
        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])

        pk_in_data_response = [int(val["pk"]) for val in data["resources"]]

        self.assertListEqual(expected_datasets, pk_in_data_response)

    def test_subsite_subsite_no_condition(self):
        """
        Subsite subsite_no_condition
            - keyword: null
            - region: null
            - group: null
            - category: null
            - resource_type: null
        Should match: all dataset defined above
        """
        url = reverse("base-resources-list", args=[self.subsite_no_condition.slug])
        expected_total = 6
        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])

    def test_subsite_geoapp(self):
        """
        Subsite subsite_geoapp
            - keyword: null
            - region: null
            - group: null
            - category: null
            - resource_type: geoapp
        Should match: None dataset defined above
        """
        url = reverse("base-resources-list", args=[self.subsite_geoapp.slug])
        expected_total = 0
        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])

        resource_type_returned = list(
            set([val["resource_type"] for val in data["resources"]])
        )

        self.assertListEqual([], resource_type_returned)

    def test_subsite_dataset(self):
        """
        Subsite subsite_datasets
            - keyword: null
            - region: null
            - group: null
            - category: null
            - resource_type: datasets
        Should match: None dataset defined above
        """
        url = reverse("base-resources-list", args=[self.subsite_datasets.slug])
        expected_total = 6
        self.client.force_login(get_user_model().objects.get(username="admin"))
        result = self.client.get(url)
        self.assertEqual(200, result.status_code)

        data = result.json()

        self.assertEqual(expected_total, data["total"])

        resource_type_returned = list(
            set([val["resource_type"] for val in data["resources"]])
        )

        self.assertListEqual(["dataset"], resource_type_returned)

    """
    View test cases
    """

    def test_bridge_view_call_the_expected_url(self):
        mocked_view = MagicMock()
        kwargs = {"view": mocked_view}

        bridge_view("request", "slug", **kwargs)

        mocked_view.assert_called_once()

    def test_subsite_home_raise_404_for_not_existing_subsite(self):
        response = self.client.get(
            reverse("subsite_home", args=["not_existing_subsite"]), follow=True
        )
        self.assertEqual(404, response.status_code)

    def test_subsite_catalogue_return_404(self):
        response = self.client.get(f"not_existing_subsite/catalogue/", follow=True)
        self.assertEqual(404, response.status_code)

    def test_subsite_home_is_redirected_to_be_rendered(self):
        response = self.client.get(
            reverse("subsite_home", args=[self.subsite_datasets.slug])
        )
        self.assertEqual(200, response.status_code)

    def test_subsite_can_add_resource_is_false(self):
        admin = get_user_model().objects.get(username='admin')
        self.client.login(username="admin", password="admin")
        response = self.client.get(
            reverse(
                "users-detail",
                args=[self.subsite_datasets.slug, admin.id]
            )
        )
        self.assertEqual(200, response.status_code)
        payload = response.json()['user']
        self.assertEqual('admin', payload.get("username"))
        self.assertListEqual([], payload.get("perms"))

    def test_subsite_can_add_resource_is_true(self):
        self.subsite_datasets.can_add_resource = True
        self.subsite_datasets.save()
        admin = get_user_model().objects.get(username='admin')
        self.client.login(username="admin", password="admin")
        response = self.client.get(
            reverse(
                "users-detail",
                args=[self.subsite_datasets.slug, admin.id]
            )
        )
        self.assertEqual(200, response.status_code)
        payload = response.json()['user']
        self.assertEqual('admin', payload.get("username"))
        self.assertListEqual(['add_resource'], payload.get("perms"))
        self.subsite_datasets.can_add_resource = False
        self.subsite_datasets.save()

    def test_api_router(self):
        '''
        Be sure that the URL refer to the subsite
        '''
        url = f"/{self.subsite_japan.slug}/api/v2/"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        for _url in response.json().values():
            self.assertTrue(f'/{self.subsite_japan.slug}/' in _url)

    def test_api_facets_have_their_own_url(self):
        '''
        Be sure that the URL refer to the subsite
        '''
        url = f"/{self.subsite_japan.slug}/api/v2/"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        self.assertTrue(f'http://localhost:8000/{self.subsite_japan.slug}/api/v2/facets' in response.json().values())

    @override_settings(SUBSITE_READ_ONLY=False)
    def test_perms_compact_for_subsite(self):
        '''
        By default only view and download perms are provided
        '''
        # The subsite from the test dosn't have any perms since the signal is not called
        url = f"/{self.subsite_japan.slug}/api/v2/resources/{self.dataset_japan.id}"
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        perms = response.json().get('resource')['perms']
        self.assertListEqual([], perms)
        
        # if we add owner and edit
        self.subsite_japan.allowed_permissions = ['owner', 'edit']
        self.subsite_japan.save()
        response = self.client.get(url)
        self.assertEqual(200, response.status_code)
        perms = response.json().get('resource')['perms']
        # only download and view are returned since the can_add_resource is FALSE by default
        self.assertSetEqual({'download_resourcebase', 'view_resourcebase'}, set(perms))
        
        # updating the can_add_resource
        self.subsite_japan.can_add_resource = True
        self.subsite_japan.save()

    def test_calling_home_should_return_all_resources(self):
        """
        If no resources has the subsite_exclusive keyword, all the resources
        should be returned in the catalog home
        """
        url = reverse('base-resources-list')
        response = self.client.get(url)
        self.assertTrue(response.json()['total'] == 6)

    def test_calling_home_should_exclude_subsite_only_resources(self):
        """
        The resources with keyword subsite_exclusive should be removed from the
        default catalog view
        """
        dataset = create_single_dataset("this_will_be_exclusive")
        kw, _ = HierarchicalKeyword.objects.get_or_create(slug="subsite_exclusive")
        dataset.keywords.add(kw)
        dataset.save()
        url = reverse('base-resources-list')
        response = self.client.get(url)
        # should be invisible to the default base resource list
        self.assertTrue(response.json()['total'] == 6)
        dataset.delete()

    def test_calling_home_should_return_even_the_exclusive_if_requested(self):
        """
        The resources with keyword subsite_exclusive should be removed from the
        default catalog view
        """
        dataset = create_single_dataset("this_will_be_exclusive")
        kw, _ = HierarchicalKeyword.objects.get_or_create(slug="subsite_exclusive")
        dataset.keywords.add(kw)
        dataset.save()
        url = reverse('base-resources-list')
        response = self.client.get(f"{url}?return_all=true")
        # should be invisible to the default base resource list
        self.assertTrue(response.json()['total'] == 7)
        dataset.delete()
