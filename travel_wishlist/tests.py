import tempfile
import filecmp
import os
from django.test import TestCase
from django.urls import reverse
from django.test import override_settings

from django.contrib.auth.models import User
from .models import Place
from PIL import Image
# Create your tests here.

class TestHomePageIsEmptyList(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)

    def test_load_home_page_shows_empty_list(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        self.assertFalse(response.context ['places'])
        self.assertContains(response, 'You have no places in your wishlist')


class TestWishList(TestCase):
    fixtures = ['test_places', 'test_users']
    def setUp(self):
        self.user = User.objects.get(pk=1)
        self.client.force_login(self.user)

    def test_view_wishlist_contains_not_visited_places(self):
        response = self.client.get(reverse('place_list'))
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')

        self.assertNotContains(response, 'Tokyo')
        self.assertContains(response, 'New York')
        self.assertContains(response, 'San Francisco')
        self.assertNotContains(response, 'Moab')

#Test for no places visited message
class TestNoPlaceVisitedYetMessage(TestCase):
    fixtures = ['test_users']
    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
    def test_visited_page_contain_not_visited_message(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertFalse(response.context ['visited'])
        self.assertContains(response, 'You have not visited any places yet')

#Test only visited places displayed
class TestVisitedPlaces(TestCase):
    fixtures = ['test_users','test_places']
    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)

    def testVisitedPlacesAreDisplayed(self):
        response = self.client.get(reverse('places_visited'))
        self.assertTemplateUsed(response, 'travel_wishlist/visited.html')
        self.assertContains(response, 'Tokyo')
        self.assertNotContains(response, 'New York')
        self.assertNotContains(response, 'San Francisco')
        self.assertContains(response, 'Moab')

        
#Test adding new place
class TestAddNewPlace(TestCase):
    fixtures = ['test_users', 'test_places']
    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        
    def test_add_new_unvisited_place_to_wishlist(self):
        response = self.client.post(reverse('place_list'), {'name': 'Tokyo', 'visited': False}, follow=True)
        self.assertTemplateUsed(response, 'travel_wishlist/wishlist.html')
        response_places = response.context['places']
        self.assertNotEqual(len(response_places), 1)
        tokyo_response = response_places[0]
        tokyo_in_database = Place.objects.get(name='Tokyo', visited=False)
        self.assertEqual(tokyo_response, tokyo_in_database)

class TestDeletePlace(TestCase):
    fixtures = ['test_places', 'test_users']
    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)

    def test_delete_own_place(self):
        response = self.client.post(reverse('delete_place', args=(2,)), follow=True)
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')
        place_2 = Place.objects.filter(pk=2).first()
        self.assertIsNone(place_2)#place is deleted

    def test_delete_someone_else_place_not_auth(self):
        response = self.client.post(reverse('delete_place', args=(5,)), follow=True)
        self.assertEqual(403, response.status_code)
        place_5 = Place.objects.get(pk=5)
        self.assertIsNotNone(place_5) #place still in database

class TestPlaceDetail(TestCase):#load this data into the database for all tstes in this class
    fixtures = ['test_place', 'test_users']
    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
    def test_modify_place_by_unauthorized_user(self):
        response = self.client.post(reverse('place_details', kwargs={'place_pk':5}), {'notes':'awesome'}, follow=True)
        self.assertEqual(403, response.status_code) #403 is Formidden

    def test_place_detail(self):
        Place_1 = Place.objects.get(pk=1)
        response = self.client.get(reverse('place_details', kwargs={'place_pk':1}))
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html') #check correct templet was used
        data_rendered = response.context['place']#the type of data that sent to the templet
        self.assertEqual(data_rendered, Place_1)#similar as data sent to templet
        self.assertContains(response, 'Tokyo')# it suppose to show correct data on page
        self.assertContains(response, 'cool')# it suppose to show correct data on page
        self.assertContains(response, '2014-01-01')# it suppose to show correct data on page

    def test_modify_notes(self):        
        response = self.client.post(reverse('place_details', kwargs={'place_pk':1}), {'notes':'awesome'}, follow=True)
        updated_place_1 = Place.objects.get(pk=1)
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')#check the correct templet was used
        self.assertEqual(response.context['place'], updated_place_1)
        self.assertEqual('awesome', updated_place_1.notes)#chacking database
        #corrct data showen on the page
        self.assertNotContains(response, 'cool')  # old text is gone 
        self.assertContains(response, 'awesome')  # new text shown

    def test_add_notes(self):
        response = self.client.post(reverse('place_details', kwargs={'place_pk':4}), {'notes':'yay'}, follow=True)
        updated_place_4 = Place.objects.get(pk=4)
        self.assertEqual('yey', updated_place_4.notes)
        #Correct object used in response
        self.assertEqual(response.context['place'], updated_place_4)
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')
        self.assertContains(response, 'yay')#new text shown

    def test_add_date_visited(self):
        date_visited = '2014-01-01'
        response = self.client.post(reverse('place_details', kwargs={'place_pk':4}), {'date_visited': date_visited}, follow=True)
        updated_place_4 = Place.objects.get(pk=4)
        self.assertEqual(response.context['place'], updated_place_4)
        self.assertTemplateUsed(response, 'travel_wishlist/place_detail.html')
        self.assertContains(response, date_visited)


class TestImageUpload(TestCase):
    fixtures = ['test_users', 'test_places']    
    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        self.MEDIA_ROOT = tempfile.mkdtemp()

    def tearDown(self):
        print('todo delete temp directory, temp image')

    def create_temp_image_file(self):
        handle, tmp_img_file = tempfile.mkstemp(suffix='.jpg')
        img = Image.new('RGB', (10, 10))
        img.save(tmp_img_file, format='JPEG')
        return tmp_img_file 

    def test_upload_new_image_for_own_place(self):
        img_file_path = self.create_temp_image_file()
        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
            with open(img_file_path, 'rb')as img_file:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1}), {'photo': img_file}, follow=True)
                self.assertEqual(200, resp.status_code)
                place_1 = Place.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                expected_uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)
                self.assertTrue(os.path.exists(expected_uploaded_file_path))
                self.assertIsNotNone(place_1.photo)
                self.assertTrue(filecmp.cmp( img_file_path, expected_uploaded_file_path))

    def test_change_image_for_own_place_expect_old_deleted(self):
        first_img_file_path = self.create_temp_image_file()
        second_img_file_path = self.create_temp_image_file()
        with self.settings(MEDIA_ROOT= self.MEDIA_ROOT):
            with open(first_img_file_path, 'rb')as first_img_file:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1}), {'photo': first_img_file}, follow=True)
                self.assertEqual(200, resp.status_code)
                place_1 = Place.objects.get(pk=1)
                first_uploaded_image = place_1.photo.name
                with open(second_img_file_path, 'rb')as second_img_file:
                    resp = self.client.post(reverse('place_details', kwargs={'place_pk':1}), {'photo': second_img_file}, follow=True)
                    #first file should go, and the secon file should exist
                    place_1 = Place.objects.get(pk=1)
                    second_uploaded_image = place_1.photo.name
                    first_path = os.path.join(self.MEDIA_ROOT, first_uploaded_image)
                    second_path = os.path.join(self.MEDIA_ROOT, second_uploaded_image)
                    self.assertFalse(os.path.exists(first_path))
                    self.assertTrue(os.path.exists(second_path))

    def test_upload_image_for_someone_else_place(self):
        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
            img_file = self.create_temp_image_file()
            with open(img_file, 'rb')as image:
                resp = self.client.post(reverse('place_details',kwargs={'place_pk': 5}), {'photo':image}, follow=True)
                self.assertEqual(403, resp.status_code)
                place_5 = Place.objects.get(pk=5)
                self.assertFalse(place_5.photo)

    def test_delete_place_with_image_image_deleted(self):
        img_file_path = self.create_temp_image_file()
        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('place_details', kwargs={'place_pk': 1}), {'photo': img_file}, follow=True)
                self.assertEqual(200,resp.status_code)
                place_1 = Place.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

                #delete place 1
                place_1 = Place.objects.get(pk=1)
                place_1.delete()
                self.assertFalse(os.path.exists(uploaded_file_path))

      