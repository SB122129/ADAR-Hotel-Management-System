# ADAR Hotel Management System

ADAR Hotel Management System (HMS) is a comprehensive web application designed to streamline and manage various operations for ADAR hotel. Built with Django, this project includes modules for room management, gym memberships, spa bookings, hall reservations, customer sign-ups, and role-based access for different staff levels.

## Key Features

### Customer Management
- **Sign-Up Options**: Customers can register via email or Google.
- **Account Verification**: For email sign-ups, a verification email is sent, requiring customers to verify their account before logging in.
- **Profile Updates**: Customers can update profile details, including profile picture and password, with appropriate field validation.
- **Room Browsing**: Customers can view room listings with detailed information and filter rooms by price or type.
- **Room Booking and Availability**: Room availability is validated to prevent double booking, and unavailable rooms prompt users to select new dates.
- **Booking Cost Calculation**: The total booking cost is calculated based on room and selected dates.
- **Payment Options**: Customers can pay via Chapa or PayPal, with a PDF receipt (including a QR code) generated on successful payment.
- **Booking Management**: View, filter, cancel, or extend bookings with real-time status updates. Extend bookings with automated cost updates and original payment processes.

### Room and Hall Management
- **Room Rating and Reviews**: View average ratings and individual reviews; customers can submit their own room ratings.
- **Hall Booking**: Customers can view and filter hall listings by price or type, check availability, and book halls with the same payment, email receipt, and QR code processes as room bookings.

### Gym Membership
- **Plan Selection**: View gym membership plans and sign up for memberships.
- **Membership Booking**: Complete the same payment, cancellation, and receipt processes as room bookings.

### Spa Services
- **Service Booking**: Customers can book spa services or packages for specific dates and times, limited to five bookings per time slot and restricted to spa working hours.
- **Consistent Payment Processing**: All bookings follow the same payment, email receipt, and QR code processes as room and gym bookings.

### Local Attractions
- **Interactive Map**: A button opens a map to view attractions in Addis Ababa.

### Admin and Staff Management
- **Account Creation and Management**: The admin can create owner accounts; owners can create and manage manager and receptionist accounts.
- **Role-Based Access Control**: Unauthorized access attempts redirect users to a "Permission Denied" page.
- **Data Visualization**: Dynamic, auto-updating charts display data on rooms, halls, gyms, spas, and users.

### Staff Operations
- **CRUD Operations**: Staff can create, update, view, and delete users, rooms, halls, gym plans, spa services, bookings, and memberships as per permissions.
- **Manual Booking Creation**: Staff can manually create bookings, cancel bookings, and update statuses.
- **PDF and QR Code Receipts**: Auto-generated receipts with QR codes are created for manual bookings and payments.
- **Search and Reporting**: Staff can search bookings, memberships, and payments; generate downloadable reports in Excel format.

### Telegram Bot Integration
- **User Interactions**: Customers can book rooms, view and pay for bookings, and cancel bookings through the Telegram bot.
- **Staff Messaging**: Staff can view and respond to user messages sent via the Telegram bot.

### Social Media Management
- **Cross-Platform Posting**: Post images and text to multiple social media platforms (Facebook, X, Instagram, Telegram) from a single page.
- **Selective Platform Posting**: Staff can select specific platforms for each post.
- **Post Management**: Search, view, and delete past posts from the admin site.

### Chatbot Integration
- **Real-Time Data Retrieval**: Staff can use an integrated chatbot for real-time data, with support for both typed messages and command shortcut buttons.

## UI/UX
### Customer Side
![room1](https://github.com/user-attachments/assets/8686559f-586e-42ab-b0e2-0a3e660ee33e)

![room2](https://github.com/user-attachments/assets/e71b677a-45aa-469b-b193-0a84d6dc69db)

![room_book](https://github.com/user-attachments/assets/4d20eef3-34ea-44a0-a78b-c282f2db2864)

![payemnt34](https://github.com/user-attachments/assets/20d7a66f-c69a-45ac-83e2-ed80c36f739b)

### Staff Side
![admin6](https://github.com/user-attachments/assets/b55090dd-375a-4379-a10e-409d044d7307)

![admin1](https://github.com/user-attachments/assets/b3d95a6b-3758-49af-8ab7-4d99ef2be3e4)

![admin2](https://github.com/user-attachments/assets/0a1d0540-162f-45c2-aea5-707218632d78)

![socila](https://github.com/user-attachments/assets/641f7395-ecff-41d2-a65c-04e467212a48)





