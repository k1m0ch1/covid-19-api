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

	b64 "encoding/base64"
	qrcodeTerminal "github.com/Baozisoftware/qrcode-terminal-go"
	whatsapp "github.com/Rhymen/go-whatsapp"
)

var wah *whatsapp.Conn

var api_summary = "https://covid-19api.herokuapp.com/"
var api_indonesia = "https://kawalcovid19.harippe.id/api/summary"

type waHandler struct {
	c *whatsapp.Conn
	startTime uint64
}

type config struct {
	covid19_api		string
	kawal_covid_api	string

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

func parsedata(url string) string {
	spaceClient := http.Client{
		Timeout: time.Second * 2,
	}

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		log.Fatal(err)
	}

	res, getErr := spaceClient.Do(req)
	if getErr != nil {
		log.Fatal(getErr)
	}

	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatal(readErr)
	}

	var result map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	reply := fmt.Sprintf("Confirmed: %.0f \nDeaths: %.0f \nRecovered: %.0f", result["confirmed"], result["deaths"], result["recovered"])

	return reply
}

func parsedataID(url string) string {
	spaceClient := http.Client{
		Timeout: time.Second * 2,
	}

	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		log.Fatal(err)
	}

	res, getErr := spaceClient.Do(req)
	if getErr != nil {
		log.Fatal(getErr)
	}

	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatal(readErr)
	}

	var result map[string]map[string]interface{}

	jsonErr := json.Unmarshal([]byte(body), &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	reply := fmt.Sprintf("Terkonfirmasi: %.0f \nMeninggal: %.0f \nSembuh: %.0f \nDalam Perawatan: %.0f\n\nUpdate terakhir %s",
		result["confirmed"]["value"], result["deaths"]["value"],
		result["recovered"]["value"], result["activeCare"]["value"], result["metadata"]["lastUpdatedAt"])

	return reply
}

//Optional to be implemented. Implement HandleXXXMessage for the types you need.
func (wh *waHandler) HandleTextMessage(message whatsapp.TextMessage) {
	// fmt.Printf("%v %v %v \n\t%v\n", message.Info.Timestamp, message.Info.Id, message.Info.RemoteJid, message.Text)
	cm1 := fmt.Sprint(b64.StdEncoding.DecodeString("eWFoeWE="))
	cmAr:= fmt.Sprint(b64.StdEncoding.DecodeString("Z2FudGVuZyBwaXNhbg=="))
	introduction := fmt.Sprintf("Halo 🤗\n\nPerkenalan saya robot covid-19 untuk mendapatkan informasi tentang covid,"+
	"panggil saya menggunakan awalan !covid\n\nPerintah yang tersedia :\n1. status (global cases)\n2. id (indonesia cases"+
	"\n3. id info"+
	"\n4. ping\n5. halo\n\nContoh : !covid status\n\n\nBantu kita di https://git.io/JvPbJ ❤️")
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
		case "ping":
			reply = "pong 🏓"
		case cm1:
			reply = cmAr
		case cm2:
			reply = cmBr
		case cm3:
			reply = cmCr
		case "status":
			reply = parsedata(fmt.Sprintf(covid19_api, "/"))
		case "id":
			if len(command) > 2{
				switch command[2] {
				case "info":
					reply = id_info
				default:
					reply = parsedataID(fmt.Sprintf(kawal_covid_api, "/api/summary"))
				}
			} else {
				reply = parsedataID(fmt.Sprintf(kawal_covid_api, "/api/summary"))
			}
		case "halo", "help", "hi", "hello":
			reply = introduction
		default:
			reply = "timeout"
		}
	}

	if len(command) > 1 && reply != "timeout" {
		<-time.After(3 * time.Second)
		go sendMessage(reply, message.Info.RemoteJid)
	}
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
	log.Printf("Trying to send message")

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
	file, err := os.Open(os.TempDir() + "/whatsappSession.gob")
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
	file, err := os.Create(os.TempDir() + "/whatsappSession.gob")
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

func getEnv(key, fallback string) string {
    value, exists := os.LookupEnv(key)
    if !exists {
        value = fallback
    }
    return value
}
