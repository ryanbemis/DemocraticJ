import SwiftUI


struct ContentView: View {
    
    @State private var image: Image? = nil
    @State private var jsonData: PollResponse? = nil
    @State private var songTitle: Text? = nil
    @State private var artistName: Text? = nil
    
    var body: some View {
        VStack {
            
            Button("Submit Song Request") {
                /*@START_MENU_TOKEN@*//*@PLACEHOLDER=Action@*/ /*@END_MENU_TOKEN@*/
            }
            .padding(.top, 20)
            .bold()
            .frame(height: 30)
            .frame(maxWidth: .infinity)
            .buttonStyle(.borderedProminent)
            .controlSize(.small)
            .buttonBorderShape(.capsule)
            .accentColor(.pink)
            .padding(.bottom, 30)
            image?
                .resizable()
                .aspectRatio(contentMode: .fill)
                //.padding(.top, 110)
                //.padding(.bottom, 0.0)
                .frame(width: 300.0, height: 300.0)
                //.padding(.bottom, 60.0)
                .cornerRadius(13)
            
            songTitle?
                .bold()
                .dynamicTypeSize(.accessibility2)
            
            artistName?
                .bold()
                .dynamicTypeSize(.large)
                .padding(.bottom, 20)
            
            Text("Would you like to add this song to the queue?")
                .bold()
                .padding(.top, 30)
                .dynamicTypeSize(.large)
            
            Button {
                handleYes()
            } label: {
                Text("Yes")
                    .bold()
                    .frame(height: 80)
                    .frame(maxWidth: .infinity)
                    }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .dynamicTypeSize(.xxxLarge)
            Button {
                handleNo()
            } label: {
                Text("No")
                    .bold()
                    .frame(height: 80)
                    .frame(maxWidth: .infinity)
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
            .dynamicTypeSize(/*@START_MENU_TOKEN@*/.xxxLarge/*@END_MENU_TOKEN@*/)
        }
        .padding()
        .onAppear {
            checkForPoll()
        }
    }
    
    func handleYes() {
        let url = URL(string: "http://localhost:8080/vote_yes")!
        
        handleEither(voteUrl: url)
    }
    
    func handleNo() {
        let url = URL(string: "http://localhost:8080/vote_no")!
        
        handleEither(voteUrl: url)
    }
    
    func handleEither(voteUrl: URL) {
        // Send the vote yes and receive the next poll
        let task = URLSession.shared.dataTask(with: voteUrl) { data, response, error in
            
            let statusCode = (response as! HTTPURLResponse).statusCode
            
            if (statusCode == 200) {
                checkForPoll()
            }
            else {
                // End of the thing, do something else here
                print("End of queue!")
            }
        }
        task.resume()
    }
    
    func checkForPoll() {
        let url = URL(string: "http://localhost:8080/cur_poll")!
        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data {
                do {
                    let decoder = JSONDecoder()
                    let decodedData = try decoder.decode(PollResponse.self, from: data)
                    
                    // Use the decoded data as needed
                    self.jsonData = decodedData
                    print(decodedData.art!)
                    loadImage(imgUrl: decodedData.art!)
                    songTitle = Text(decodedData.name!)
                    artistName = Text(decodedData.artist!)
                } catch {
                    print("JSON Decoding Failed: \(error)")
                }
            } else if let error = error {
                print("HTTP Request Failed \(error)")
            }
        }

        task.resume()
    }
    
    
    func loadImage(imgUrl: String) {
        let url = URL(string: imgUrl)!

        let task = URLSession.shared.dataTask(with: url) { data, response, error in
            if let data = data {
                if let uiImage = UIImage(data: data) {
                    let newImage = Image(uiImage: uiImage)
                    DispatchQueue.main.async {
                        self.image = newImage
                    }
                }
            } else if let error = error {
                print("HTTP Request Failed \(error)")
            }
        }

        task.resume()
    }
}

struct PollResponse: Codable {
    let art: String?
    let id: String?
    let name: String?
    let artist: String?
}


struct ContentView_Previews: PreviewProvider {
    static var previews: some View {
        ContentView()
    }
}
