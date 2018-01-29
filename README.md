# auto_emojiboard
A keyboard with automatic emoji reccomendations

# Inspiration
The recent launch of the iPhoneX brought with it the "indispensable" tool called Animoji, which enabled iPhoneX users to map their face to 3D animated characters and send them through messaging platforms.

We from Team Makerforce, wanted to create something that allows Android users to use emojis more expressively and easily with lesser browsing through never ending lists of smiley, winky and sad faces. We believe that such a tool would enable more Android users to express themselves with ease while also proving to be more useful than Animoji as a platform for easy sharing of emotions. And this is why we created EmojiBoard, the world's first Android keyboard with machine learning and emotion recognition built in.

![img/keyboard.jpg]
![img/settings.jpg]

# What it does
EmojiBoard uses the front-facing camera on any Android phone to capture your expressions in real time and translates those expressions into what would be the most appropriate emojis for that moment. This allows users to simply feel and send those feelings to the opposing party without any scrolling or searching for just the right emoji. These recommended emojis are displayed within your keyboard in a top bar, allowing you to text your emotions with the single press of a button.

# How we built it
EmojiBoard was built from a fork of the AOSP default google keyboard. We modified the source code of the keyboard and added support for the top bar which displays emoji suggestions. The phone's front facing camera streams photos of the user while the keyboard is activated to a remote server, which analyzes the picture and sends back the detected emotion on the users face. This is achieved through a convolutional neural network. This emotion is used to choose and display the appropriate emoji suggestions.

# Challenges we ran into
We wanted to implement hand gesture detection but it was hard because of the face of the person being in view. This is because hand detection relies on skin detection as well which the person's face also fulfills.
Convolutionary neural networks are slow
Building the android keyboard for the first time took multiple hours of debugging
Limited resources on the phone means that most of the processing needed to be done on the server side
What we learned
We learnt how to build custom android keyboards and how to interface it to a convolutional neural net without significant processing time and lag.

# What's next for EmojiBoard
We are planning to add more support for a greater variety of emotions so that the emoji suggestions are more appropriate. Additionally, the current training dataset using mostly American people which makes it inaccurate with Asian faces. We will need to expand the range of our training dataset to make it more accurate in all use cases. Lastly, we want to add support for hand gesture recognition so that hand gestures can also be translated to their respective hand gesture emojis.
