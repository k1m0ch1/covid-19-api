package main

import (
	"encoding/gob"
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"
	"time"
	"strings"
	"encoding/json"
	"net/http"
	"io/ioutil"
	"math/rand"

	b64 "encoding/base64"
	qrcodeTerminal "github.com/Baozisoftware/qrcode-terminal-go"
	whatsapp "github.com/Rhymen/go-whatsapp"
)

var wah *whatsapp.Conn

type waHandler struct {
	c *whatsapp.Conn
	startTime uint64
}

func parseNews(endpoint string) string {

	url := "https://covid19-api.yggdrasil.id/news%s"
	url = fmt.Sprintf(url, endpoint)

	body := reqUrl(url)

	var result []map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatal("Break point 4 %s %s",jsonErr, result)
	}
	reply := "Top Headlines\n\n"
	for i := range result {
		reply = reply + fmt.Sprintf("%s\n%s\n\n", result[i]["title"], result[i]["url"])
	}

	return reply + "Cermat dalam mengamati berita dan hindari hoaks\nBantu kami di https://git.io/JvPbJ ❤️"
}

func parsedataCountries(country_id string) string {
	url := "https://covid19-api.yggdrasil.id/countries/%s"
	url = fmt.Sprintf(url, country_id)

	body := reqUrl(url)

	var result []map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	c := 0.0
	d := 0.0
	r := 0.0

	for i := range result {
		c += result[i]["confirmed"].(float64)
		d += result[i]["deaths"].(float64)
		r += result[i]["recovered"].(float64)
	}

	return fmt.Sprintf("%s\n\nConfirmed: %.0f\nDeaths: %.0f\nRecovered: %.0f", countries(strings.ToUpper(country_id)), c, d, r)

}

func parsedata(url string) string {
	body := reqUrl(url)

	var result map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	reply := fmt.Sprintf("Global Cases\n\nConfirmed: %.0f \nDeaths: %.0f \nRecovered: %.0f", result["confirmed"], result["deaths"], result["recovered"])

	return reply
}

func parsedataID(url string) string {
	body := reqUrl(url)

	var result map[string]map[string]interface{}

	jsonErr := json.Unmarshal([]byte(body), &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	t1, e := time.Parse(
        time.RFC3339,
		fmt.Sprintf("%s", result["metadata"]["lastUpdatedAt"]))
	e=e

	reply := fmt.Sprintf("Terkonfirmasi: %.0f \nMeninggal: %.0f \nSembuh: %.0f \nDalam Perawatan: %.0f\n\nUpdate terakhir %s",
		result["confirmed"]["value"], result["deaths"]["value"],
		result["recovered"]["value"], result["activeCare"]["value"], t1.Add(7*time.Hour).Format("02 Jan 06 15:04"))

	return reply
}

//Optional to be implemented. Implement HandleXXXMessage for the types you need.
func (wh *waHandler) HandleTextMessage(message whatsapp.TextMessage) {
	// fmt.Printf("%v %v %v \n\t%v\n", message.Info.Timestamp, message.Info.Id, message.Info.RemoteJid, message.Text)
	cm1 := fmt.Sprint(b64.StdEncoding.DecodeString("eWFoeWE="))
	cmAr:= fmt.Sprint(b64.StdEncoding.DecodeString("Z2FudGVuZyBwaXNhbg=="))
	introduction := fmt.Sprintf("Halo 🤗\n\nPerkenalan saya robot covid-19 untuk mendapatkan informasi tentang covid,"+
	"panggil saya menggunakan awalan !covid\n\nPerintah yang tersedia :\n1. status (global cases)\n"+
	"2. news (top headline news)\n3. id (indonesia cases"+
	"\n4. id info\n5. id news(top headline news indonesia)"+
	"\n7. halo\n\nContoh : !covid status\n\nBantu kami di https://git.io/JvPbJ ❤️")
	cm2:= fmt.Sprint(b64.StdEncoding.DecodeString("eW9hbmE="))
	cmBr:= fmt.Sprint(b64.StdEncoding.DecodeString("bXkgcm9vdCBvZiBldmVyeXRoaW5n"))
	id_info := fmt.Sprintf("🔔Informasi Corona seputar Indonesia🔔\n"+
	"- Hotline COVID-19 Telepon 119 Ext 9\n\n"+
	"- https://infeksiemerging.kemkes.go.id/ untuk Spot Kasus COVID-19\n\n"+
	"- https://pikobar.jabarprov.go.id/ Pusat Informasi & Koordinasi COVID-19 Provinsi Jawa Barat\n\n"+
	"- https://kawalcovid19.id/ Kawal informasi seputar COVID-19 secara tepat dan akurat.\n\n")
	cm3:= fmt.Sprint(b64.StdEncoding.DecodeString("eWdnZHJhc2ls"))
	cmCr:= fmt.Sprint(b64.StdEncoding.DecodeString("bXkgcGVhY2g="))

	if !strings.Contains(strings.ToLower(message.Text), "!covid") || message.Info.Timestamp < wh.startTime {
		return
	}

	covid19_api := "https://covid19-api.yggdrasil.id%s"
	kawal_covid_api := "https://kawalcovid19.harippe.id%s"

	command := strings.Fields(message.Text)
	reply := "timeout"
	if len(command) > 1 {
		switch command[1] {
		case "news":
			reply = parseNews("")
		case "status":
			if len(command) > 2{
				reply = parsedataCountries(command[2])
			} else {
				reply = parsedata(fmt.Sprintf(covid19_api, "/"))
			}
		case "id":
			if len(command) > 2{
				switch command[2] {
				case "info":
					reply = id_info
				case "news":
					reply = parseNews("/id")
				default:
					reply = parsedataID(fmt.Sprintf(kawal_covid_api, "/api/summary"))
				}
			} else {
				reply = parsedataID(fmt.Sprintf(kawal_covid_api, "/api/summary"))
			}
		case "halo", "help", "hi", "hello":
			reply = introduction
		case "ping":
			reply = "pong 🏓"
		case cm1:
			reply = cmAr
		case cm2:
			reply = cmBr
		case cm3:
			reply = cmCr
		default:
			reply = "timeout"
		}
	}

	if len(command) > 1 && reply != "timeout" {
		<-time.After(time.Duration(rand.Intn(7 - 3) + 3) * time.Second)
		go sendMessage(reply, message.Info.RemoteJid)
	}
}

func countries(code string) string{
	url := "https://covid19-api.yggdrasil.id/countries"
	body := reqUrl(url)

	var result map[string]map[string]interface{}

	jsonErr := json.Unmarshal([]byte(body), &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	for key, val := range result["countries"] {
		if val == code {
			return key
		}
	}

	return "Not Found"
}

func main() {
	//create new WhatsApp connection
	wac, err := whatsapp.NewConn(5 * time.Second)
	if err != nil {
		log.Fatalf("error creating connection: %v\n", err)
	}

	//Add handler
	wac.AddHandler(&waHandler{wac, uint64(time.Now().Unix())})

	//login or restore
	if err := login(wac); err != nil {
		log.Fatalf("error logging in: %v\n", err)
	}

	wah = wac

	//verifies phone connectivity
	pong, err := wac.AdminTest()

	if !pong || err != nil {
		log.Fatalf("error pinging in: %v\n", err)
	}

	c := make(chan os.Signal, 1)
	signal.Notify(c, os.Interrupt, syscall.SIGTERM)
	<-c

	//Disconnect safe

	fmt.Println("Shutting down now.")
	session, err := wac.Disconnect()
	if err != nil {
		log.Fatalf("error disconnecting: %v\n", err)
	}
	if err := writeSession(session); err != nil {
		log.Fatalf("error saving session: %v", err)
	}
}

func sendMessage(message string, RJID string) {
	msg := whatsapp.TextMessage{
		Info: whatsapp.MessageInfo{
			RemoteJid: RJID,
		},
		Text:        message,
	}

	msgId, err := wah.Send(msg)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error sending message: %v", err)
		os.Exit(1)
	} else {
		fmt.Println("Message Sent -> ID : " + msgId)
	}
}

func login(wac *whatsapp.Conn) error {
	//load saved session
	session, err := readSession()
	if err == nil {
		//restore session
		session, err = wac.RestoreWithSession(session)
		if err != nil {
			return fmt.Errorf("restoring failed: %v\n", err)
		}
		log.Println(session.Wid)
	} else {
		//no saved session -> regular login
		qr := make(chan string)
		go func() {
			terminal := qrcodeTerminal.New()
			terminal.Get(<-qr).Print()
		}()
		session, err = wac.Login(qr)
		if err != nil {
			return fmt.Errorf("error during login: %v\n", err)
		}
	}

	//save session
	err = writeSession(session)
	if err != nil {
		return fmt.Errorf("error saving session: %v\n", err)
	}
	return nil
}

func readSession() (whatsapp.Session, error) {
	session := whatsapp.Session{}
	log.Println("Trying to get the session " + getSessionName())
	file, err := os.Open(getSessionName())
	if err != nil {
		return session, err
	}
	defer file.Close()
	decoder := gob.NewDecoder(file)
	err = decoder.Decode(&session)
	if err != nil {
		return session, err
	}
	return session, nil
}

func writeSession(session whatsapp.Session) error {
	file, err := os.Create(getSessionName())
	if err != nil {
		return err
	}
	defer file.Close()
	encoder := gob.NewEncoder(file)
	err = encoder.Encode(session)
	if err != nil {
		return err
	}
	return nil
}

func getSessionName() string{
	mydir, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
	}
	if _, err := os.Stat(mydir + "/session"); os.IsNotExist(err) {
		os.MkdirAll(mydir + "/session", os.ModePerm)
	}
	sessionName := ""
	if len(os.Args) == 1 {
		sessionName =  mydir + "/session" + "/whatsappSession.gob"
	}else{
		sessionName = mydir + "/session/" + os.Args[1] + ".gob"
	}

	return sessionName
}

//HandleError needs to be implemented to be a valid WhatsApp handler
func (h *waHandler) HandleError(err error) {

	if e, ok := err.(*whatsapp.ErrConnectionFailed); ok {
		log.Printf("Connection failed, underlying error: %v", e.Err)
		log.Println("Waiting 30sec...")
		<-time.After(30 * time.Second)
		log.Println("Reconnecting...")
		err := h.c.Restore()
		if err != nil {
			log.Fatalf("Restore failed: %v", err)
		}
	} else {
		log.Printf("error occoured: %v\n", err)
	}
}

func reqUrl(url string) []byte{
	spaceClient := http.Client{
		Timeout: time.Second * 2,
	}

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		log.Fatal("Break point 1 %s", err)
	}

	res, getErr := spaceClient.Do(req)
	if getErr != nil {
		log.Fatal("Break point 2 %s",getErr)
	}

	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatal("Break point 3 %s",readErr)
	}

	return body
}
