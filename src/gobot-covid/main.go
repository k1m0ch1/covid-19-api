package main

import (
	"encoding/gob"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"math/rand"
	"net/http"
	"os"
	"os/signal"
	"strings"
	"syscall"
	"time"
	"math"

	b64 "encoding/base64"
	qrcodeTerminal "github.com/mdp/qrterminal/v3"
	whatsapp "github.com/Rhymen/go-whatsapp"
)

var wah *whatsapp.Conn

type waHandler struct {
	c         *whatsapp.Conn
	startTime uint64
}

var url = "https://covid19-api.yggdrasil.id%s"


func parseNews(endpoint string) string {
	link := fmt.Sprintf(url + "%s", "/news", endpoint)
	body, err:= reqUrl(link)
	if err >= 400 {
		log.Printf("Error, %d when access %s ", err, link)
		return "timeout"
	}

	var result []map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatalf("Break point 4 %s %s", jsonErr, result)
	}

	reply := "Top Headlines\n\n"
	for i := range result {
		reply = reply + fmt.Sprintf("%s\n%s\n\n", result[i]["title"], result[i]["url"])
	}

	return reply + "Cermat dalam mengamati berita dan hindari hoaks\nBantu kami di https://git.io/JvPbJ ❤️"
}

func parsedataCountries(country_id string) string {
	link := fmt.Sprintf(url + "%s", "/countries/", country_id)
	body, err := reqUrl(link)
	if err >= 400 {
		log.Printf("Error, %d when access %s ", err, link)
		return "timeout"
	}

	var result []map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	c, d, r := 0.0, 0.0, 0.0

	for i := range result {
		c += result[i]["confirmed"].(float64)
		d += result[i]["deaths"].(float64)
		r += result[i]["recovered"].(float64)
	}

	return fmt.Sprintf("*%s*\n\nConfirmed: %.0f\nDeaths: %.0f\nRecovered: %.0f", countries(strings.ToUpper(country_id)), c, d, r)

}

func parseHotline(search string) string {
	link := fmt.Sprintf(url + "%s", "/id/hotline/", search)
	body, err := reqUrl(link)
	if err >= 400 {
		log.Printf("Error, %d when access %s ", err, link)
		return "timeout"
	}

	var result []map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	reply := ""

	for i := range result {
		cc := result[i]["callCenter"].([]interface{})
		call := ""
		for x := range cc {
			call += fmt.Sprintf("%s, ", cc[x])
		}

		hh := result[i]["hotline"].([]interface{})
		hot := ""
		for y := range hh {
			hot += fmt.Sprintf("%s, ", hh[y])
		}
		reply += fmt.Sprintf("\n*%s*\nCall Center: %s\nHotline: %s\n",
			result[i]["kota"], call, hot)
	}

	return reply
}

func parsedata() string {
	link := fmt.Sprintf(url, "/")
	body, err := reqUrl(link)
	if err >= 400 {
		log.Printf("Error, %d when access %s ", err, link)
		return "timeout"
	}

	var result map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	reply := fmt.Sprintf("*Global Cases*\n\nConfirmed: %.0f \nDeaths: %.0f \nRecovered: %.0f", result["confirmed"], result["deaths"], result["recovered"])

	return reply
}

func parsedataID() string {
	link := fmt.Sprintf(url, "/id/")
	body, err := reqUrl(link)
	if err >= 400 {
		log.Printf("Error, %d when access %s ", err, link)
		return "timeout"
	}

	var result map[string]map[string]interface{}

	jsonErr := json.Unmarshal([]byte(body), &result)
	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	t1, _ := time.Parse(
		time.RFC3339,
		fmt.Sprintf("%s+00:00", result["metadata"]["last_updated"]))

	reply := fmt.Sprintf("*Indonesia*\n\nTerkonfirmasi: %.0f *(+%.0f)*\nMeninggal: %.0f *(+%.0f)*\nSembuh: %.0f *(+%.0f)*" +
		"\nDalam Perawatan: %.0f *(+%.0f)*\n\nUpdate terakhir %s\n" +
		"Data Ini Diambil Dari https://kawalcovid19.id/ ",
		result["confirmed"]["value"], result["confirmed"]["diff"],
		result["deaths"]["value"], result["deaths"]["diff"],
		result["recovered"]["value"], result["recovered"]["diff"],
		result["active_care"]["value"], result["active_care"]["diff"],
		t1.Add(7*time.Hour).Format("02 Jan 2006 15:04"))

	return reply
}

func parseDataIDProvince(state string) string {
	body, err := reqUrl(fmt.Sprintf(url + "%s", "/id/", state))
	if err >= 400 {
		log.Printf("Error, %d", err)
		return "timeout"
	}

	var result map[string]map[string]interface{}

	jsonErr := json.Unmarshal(body, &result)

	if jsonErr != nil {
		log.Fatal(jsonErr)
	}

	if _, ok := result["message"]; ok {
		return "Belum Tersedia"
	}

	if state != "jabar" {
		return fmt.Sprintf("*%s* \n\nSembuh: %.0f \n" +
			"Positif: %.0f \nTotal Meninggal: %.0f \n" +
			"\nSumber data %s ",
			strings.Title(strings.ToUpper(state)), result["total_sembuh"]["value"].(float64),
			result["total_positif_saat_ini"]["value"].(float64),
			result["total_meninggal"]["value"].(float64), result["source"]["value"])
	}else{
		total_meninggal_diff := result["total_meninggal"]["diff"].(float64)
		total_positif_saat_ini_diff := result["total_positif_saat_ini"]["diff"].(float64)
		total_sembuh_diff := result["total_sembuh"]["diff"].(float64)

		return fmt.Sprintf("*%s* \n\nSembuh: %.0f *(%s)*\n" +
			"Positif: %.0f *(%s)*\nTotal Meninggal: %.0f *(%s)* \n" +
			"\nProses Pemantauan: %.0f \nProses Pengawasan: %.0f \nSelesai Pemantauan: %.0f " +
			"\nSelesai Pengawasan: %.0f \nODP: %.0f \nPDP: %.0f " +
			"\n\nUpdate terakhir %s" +
			"\n\nSumber data %s ",
			strings.Title(strings.ToUpper(state)), result["total_sembuh"]["value"].(float64), printPositive(total_sembuh_diff),
			result["total_positif_saat_ini"]["value"].(float64), printPositive(total_positif_saat_ini_diff),
			result["total_meninggal"]["value"].(float64), printPositive(total_meninggal_diff),
			result["proses_pemantauan"]["value"], result["proses_pengawasan"]["value"], result["selesai_pemantauan"]["value"],
			result["selesai_pengawasan"]["value"], result["total_odp"]["value"], result["total_pdp"]["value"],
			result["tanggal"]["value"], result["source"]["value"])
	}
}


//Optional to be implemented. Implement HandleXXXMessage for the types you need.
func (wh *waHandler) HandleTextMessage(message whatsapp.TextMessage) {
	// fmt.Printf("%v %v %v \n\t%v\n", message.Info.Timestamp, message.Info.Id, message.Info.RemoteJid, message.Text)
	cm1 := fmt.Sprint(b64.StdEncoding.DecodeString("eWFoeWE="))
	cmAr := fmt.Sprint(b64.StdEncoding.DecodeString("Z2FudGVuZyBwaXNhbg=="))
	introduction := fmt.Sprintf("*Halo* 🤗\n\nPerkenalan saya robot covid-19 untuk mendapatkan informasi tentang covid," +
		"panggil saya menggunakan awalan !covid\n\nPerintah yang tersedia :\n1. status (global cases)\n" +
		"2. hotline\n3. news \n4. id (indonesia cases)" +
		"\n5. id <jabar,jakarta,banten,bali,yogya>" +
		"\n6. id info\n7. id news (top headline news indonesia)" +
		"\n8. halo\n\nContoh : !covid id jabar\n" +
		"\n\nBantu kami di https://git.io/JvPbJ ❤️")
	cm2 := fmt.Sprint(b64.StdEncoding.DecodeString("eW9hbmE="))
	cmBr := fmt.Sprint(b64.StdEncoding.DecodeString("bXkgcm9vdCBvZiBldmVyeXRoaW5n"))
	id_info := fmt.Sprintf("🔔Informasi Corona seputar Indonesia🔔\n" +
		"- Hotline COVID-19 Telepon 119 Ext 9\n\n" +
		"- Jika sakit maka, tinggal dirumah, gunakan master\n\n" +
		"- https://infeksiemerging.kemkes.go.id/ untuk Spot Kasus COVID-19\n\n" +
		"- https://pikobar.jabarprov.go.id/ Pusat Informasi & Koordinasi COVID-19 Provinsi Jawa Barat\n\n" +
		"- https://kawalcovid19.id/ Kawal informasi seputar COVID-19 secara tepat dan akurat.\n\n")
	cm3 := fmt.Sprint(b64.StdEncoding.DecodeString("eWdnZHJhc2ls"))
	cmCr := fmt.Sprint(b64.StdEncoding.DecodeString("bXkgcGVhY2g="))

	if !strings.Contains(strings.ToLower(message.Text), "!covid") || message.Info.Timestamp < wh.startTime {
		return
	}

	command := strings.Fields(message.Text)
	reply := "timeout"
	if len(command) > 1 {
		switch command[1] {
		case "news":
			reply = parseNews("")
		case "hotline":
			if len(command) > 2 {
				reply = parseHotline(command[2])
			}else{
				reply = parseHotline("")
			}
		case "status":
			if len(command) > 2 {
				reply = parsedataCountries(command[2])
			} else {
				reply = parsedata()
			}
		case "id":
			if len(command) > 2 {
				switch command[2] {
				case "info":
					reply = id_info
				case "news":
					reply = parseNews("/id")
				default:
					reply = parseDataIDProvince(command[2])
				}
			} else {
				reply = parsedataID()
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
		<-time.After(time.Duration(rand.Intn(4-2)+2) * time.Second)
		go sendMessage(reply, message.Info.RemoteJid)
	}
}

func countries(code string) string {
	body, err:= reqUrl(fmt.Sprintf(url, "/countries"))
	if err >= 400 {
		log.Printf("Error, %d", err)
		return "timeout"
	}

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
	wac.SetClientVersion(0, 4, 2080)
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
		Text: message,
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
		go func(){
			config := qrcodeTerminal.Config{
				Level: qrcodeTerminal.L,
				Writer: os.Stdout,
				BlackChar: qrcodeTerminal.BLACK,
				WhiteChar: qrcodeTerminal.WHITE,
				QuietZone: 1,
			}
			qrcodeTerminal.GenerateWithConfig(<-qr, config)
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

func getSessionName() string {
	mydir, err := os.Getwd()
	if err != nil {
		fmt.Println(err)
	}
	if _, err := os.Stat(mydir + "/session"); os.IsNotExist(err) {
		os.MkdirAll(mydir+"/session", os.ModePerm)
	}
	sessionName := ""
	if len(os.Args) == 1 {
		sessionName = mydir + "/session" + "/whatsappSession.gob"
	} else {
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

func reqUrl(url string) ([]byte, int) {

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		log.Fatalf("Break point 1 %s", err)
	}

	req.Header.Set("User-Agent", "gobot-covid19/2.0")

	client := &http.Client{}
	res, err := client.Do(req)
	if err != nil {
			log.Fatalln(err)
	}

	if res.StatusCode >= 400 {
		return nil, res.StatusCode
	}

	body, readErr := ioutil.ReadAll(res.Body)
	if readErr != nil {
		log.Fatalf("Break point 3 %s", readErr)
	}

	return body, 200
}


func printPositive(num float64) string {
	if math.Signbit(num) {
		return fmt.Sprintf("%.0f", num)
	}
	return fmt.Sprintf("+%.0f", num)
}

